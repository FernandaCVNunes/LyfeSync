# app_LyfeSync/views/_aux_logic.py
import re
import calendar
from datetime import timedelta, date
from decimal import Decimal

# Imports Django
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.contrib import messages
from django.forms.models import modelformset_factory
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.utils import timezone 

# ===================================================================
# MOCKS DE CLASSES E FUNÇÕES (Necessário para Views de Exportação)
# Estes mocks simulam a existência dos seus modelos e forms reais.
# ===================================================================

# --- Mock de Usuário (Necessário para @login_required) ---
class MockUser:
    """Simulação de um objeto User para testes sem autenticação."""
    def __init__(self, username="mock_user"):
        self.username = username
        # Simula o ID do usuário para o MockManager
        self.id = 1 if username == "user1" else 2 

    @property
    def is_authenticated(self):
        return True

    def __repr__(self):
        return f"MockUser('{self.username}')"


# --- Mock do Modelo Gratidao ---
class Gratidao:
    # Gerenciador será mockado abaixo
    objects = None 
    DoesNotExist = Exception # Exceção padrão do Django

    def __init__(self, idgratidao=None, descricaogratidao="", usuario=None, data=None):
        self.idgratidao = idgratidao
        # Nome do campo ajustado para corresponder ao uso em crud_views.py
        self.descricaogratidao = descricaogratidao 
        self.usuario = usuario.username if hasattr(usuario, 'username') else usuario
        self.data = data or timezone.localdate()
        self.pk = idgratidao # Campo primário

    def save(self):
        # Simula a persistência
        print(f"Salvando Gratidão ID: {self.pk}, Descrição: {self.descricaogratidao}")
    
    def delete(self):
        # Simula a exclusão
        print(f"Deletando Gratidão ID: {self.pk}")

    # Método de representação para debug
    def __repr__(self):
        return f"Gratidao(id={self.idgratidao}, data={self.data}, user={self.usuario})"

# --- Mock do Formulário GratidaoForm ---
# Simula a funcionalidade básica para fins de teste de view
class GratidaoForm:
    def __init__(self, data=None, instance=None, **kwargs):
        self.data = data or {}
        self.instance = instance
        # Adiciona o objeto instance como 'instance' do formulário para formsets
        if instance:
            # Popula os dados iniciais do formulário para o formset
            self.data['descricaogratidao'] = instance.descricaogratidao
            if instance.data:
                self.data['data'] = instance.data.isoformat()
        
    def is_valid(self):
        # Validação simples: a descrição deve existir e não ser vazia (para FormSet)
        descricao = self.data.get('descricaogratidao', self.data.get('descricaogratidao_0'))
        return bool(descricao)
    
    @property
    def changed_data(self):
        # Mock para simular se houve alteração (importante para formset.save)
        return ['descricaogratidao']

    @property
    def instance(self):
        return self._instance

    @instance.setter
    def instance(self, value):
        self._instance = value

    def save(self, commit=True):
        # O mock aqui precisa ser robusto para FormSet (criação e atualização)
        
        # 1. Recupera os dados do POST (o FormSet injeta os dados nos campos)
        # Assumimos que o nome do campo é 'descricaogratidao' e 'data'
        descricao = self.data.get('descricaogratidao')
        data_str = self.data.get('data')

        if data_str:
            try:
                data_obj = date.fromisoformat(data_str)
            except ValueError:
                data_obj = timezone.localdate()
        else:
            data_obj = timezone.localdate() # Valor padrão

        if self.instance and self.instance.pk:
            # Atualização
            self.instance.descricaogratidao = descricao or self.instance.descricaogratidao
            self.instance.data = data_obj or self.instance.data
            if commit:
                self.instance.save()
            return self.instance
        else:
            # Criação
            new_instance = Gratidao(
                descricaogratidao=descricao,
                data=data_obj,
                # O usuário será definido na view (commit=False)
                idgratidao=None 
            )
            if commit:
                new_instance.save()
            return new_instance

# --- Mock do QuerySet e Gerenciador de Gratidão (ORM) ---
class GratidaoQuerySet:
    def __init__(self, items):
        self.items = list(items)

    def filter(self, **kwargs):
        filtered_items = self.items
        
        # Filtragem por Usuário
        if 'usuario' in kwargs:
            filter_user_or_obj = kwargs['usuario']
            user_identifier = filter_user_or_obj.username if hasattr(filter_user_or_obj, 'username') else filter_user_or_obj
            filtered_items = [i for i in filtered_items if i.usuario == user_identifier]

        # Filtragem por Data
        if 'data' in kwargs:
            # Assumindo que 'data' é um objeto date puro
            filtered_items = [i for i in filtered_items if i.data == kwargs['data']]
            
        # Retorna uma nova instância de QuerySet com os itens filtrados
        return GratidaoQuerySet(filtered_items)

    def order_by(self, *args):
        # Mock de ordenação simples (o código real faria a ordenação)
        # Se for ordenado por data descendente, inverte a lista (simples)
        if args and '-data' in args:
            self.items.sort(key=lambda x: x.data, reverse=True)
        return self

    def first(self):
        return self.items[0] if self.items else None

    def __len__(self):
        return len(self.items)

    # Permite iteração (for item in queryset)
    def __iter__(self):
        return iter(self.items)
    
    # Permite slice e indexação
    def __getitem__(self, key):
        if isinstance(key, slice):
            return self.items[key.start:key.stop:key.step]
        return self.items[key]

# Gerenciador que simula Gratidao.objects
class GratidaoManager:
    def __init__(self):
        self.mock_data = self._initialize_data()

    def _initialize_data(self):
        hoje = timezone.localdate()
        yesterday = hoje - timedelta(days=1)
        two_days_ago = hoje - timedelta(days=2)
        
        data = [
            # Registros de Hoje (em ordem de criação para teste de 'first()')
            Gratidao(idgratidao=4, descricaogratidao="Gratidão 4 de Hoje (Mais Recente)", usuario="user1", data=hoje),
            Gratidao(idgratidao=3, descricaogratidao="Gratidão 3 de Hoje", usuario="user1", data=hoje),
            Gratidao(idgratidao=2, descricaogratidao="Gratidão 2 de Hoje", usuario="user1", data=hoje),

            # Registros Antigos
            Gratidao(idgratidao=1, descricaogratidao="Gratidão 1 de Ontem", usuario="user1", data=yesterday),
            Gratidao(idgratidao=5, descricaogratidao="Gratidão 5 de Dois Dias Atrás", usuario="user1", data=two_days_ago),
            Gratidao(idgratidao=6, descricaogratidao="Gratidão de Outro Usuário", usuario="user2", data=hoje),
        ]
        # Garante que os IDs são únicos
        current_max_id = max(item.idgratidao for item in data) if data else 0

        # Ajusta os IDs dos mocks para que novas criações não gerem conflitos
        for item in data:
            if item.idgratidao is None:
                current_max_id += 1
                item.idgratidao = current_max_id
                item.pk = current_max_id
                
        return data

    def filter(self, **kwargs):
        qs = GratidaoQuerySet(self.mock_data)
        return qs.filter(**kwargs)

    def get(self, pk, usuario):
        # Ajuste do Mock: Determina o identificador (username)
        user_identifier = usuario.username if hasattr(usuario, 'username') else usuario
        
        for item in self.mock_data:
            if item.idgratidao == pk and item.usuario == user_identifier:
                return item
        raise Gratidao.DoesNotExist(f"Gratidão ID {pk} não encontrada.")

# Associa o mock ao Modelo
Gratidao.objects = GratidaoManager()

# -------------------------------------------------------------------
# LÓGICA AUXILIAR PRINCIPAL
# -------------------------------------------------------------------

# VARIÁVEL DE REGEX CORRIGIDA:
DICA_DELIMITADOR_REGEX = r'^\[DICA ID:(\d+)\]\s*(.*)$'

def extract_dica_info(descricaohumor):
    """
    Tenta extrair o ID da dica ([DICA ID:X]) e retorna a descrição limpa do usuário.
    (Função mantida com nome original 'humor' para compatibilidade com o trecho do usuário.)
    """
    if not descricaohumor:
        return None, ""
        
    descricaohumor = descricaohumor.strip()
    match = re.match(DICA_DELIMITADOR_REGEX, descricaohumor)
    
    if match:
        dica_id_salva = int(match.group(1)) # Grupo 1: O ID da dica (X em [DICA ID:X])
        descricao_usuario_original = match.group(2).strip() # Grupo 2: O restante da descrição
    else:
        dica_id_salva = None
        descricao_usuario_original = descricaohumor
        
    return dica_id_salva, descricao_usuario_original

def rebuild_descricaohumor(dica_id, descricao_usuario):
    """
    Reconstrói o campo 'descricaohumor' adicionando a tag [DICA ID:X] de volta.
    """
    descricao_usuario = descricao_usuario.strip()
    if dica_id:
        # Garante o formato: [DICA ID:X] <Descrição do Usuário>
        return f"[DICA ID:{dica_id}] {descricao_usuario}"
    return descricao_usuario

# --- Correção de Referência ---
def extract_dica_gratidao_info(descricaogratidao):
    """
    Extrai o ID da dica ([DICA ID:X]) e a descrição limpa do usuário do campo de Gratidão.
    """
    return extract_dica_info(descricaogratidao) 

def rebuild_descricaogratidao(dica_id, descricao_usuario):
    """
    CORRIGIDO: Reconstrói o campo 'descricaogratidao' chamando a função auxiliar correta.
    (O original tinha um erro de recursão/referência incorreta)
    """
    return rebuild_descricaohumor(dica_id, descricao_usuario)

# -------------------------------------------------------------------
# LÓGICA AUXILIAR DIVERSA (Manter para evitar erros de dependência)
# -------------------------------------------------------------------

def _get_report_date_range(request, hoje, default_periodo=None):
    """
    Calcula o intervalo de datas (inicio e fim) com base nos parâmetros GET.
    """
    
    if default_periodo in ['mensal', 'semanal', 'anual']:
        periodo = default_periodo
    else:
        periodo = request.GET.get('periodo', 'mensal') 

    try:
        mes_param = int(request.GET.get('mes', hoje.month))
    except (ValueError, TypeError):
        mes_param = hoje.month
        
    try:
        ano_param = int(request.GET.get('ano', hoje.year))
    except (ValueError, TypeError):
        ano_param = hoje.year

    try:
        data_referencia = date(year=ano_param, month=mes_param, day=1)
    except ValueError:
        data_referencia = hoje
    
    if periodo == 'semanal':
        inicio_semana = hoje - timedelta(days=hoje.weekday())
        data_inicio = inicio_semana
        data_fim = inicio_semana + timedelta(days=6)
        
    elif periodo == 'anual':
        data_inicio = data_referencia.replace(month=1, day=1)
        data_fim = data_referencia.replace(month=12, day=31)
        
    else: # 'mensal' ou fallback
        _, ultimo_dia_mes = calendar.monthrange(data_referencia.year, data_referencia.month)
        data_inicio = data_referencia.replace(day=1)
        data_fim = data_referencia.replace(day=ultimo_dia_mes)
        periodo = 'mensal'

    return data_inicio, data_fim, data_referencia, periodo, mes_param, ano_param

# Mocks para Humor (mantidos)
class HumorTipo:
    def __init__(self, pk, icone):
        self.pk = pk
        self.icone = icone

    @staticmethod
    def objects_all():
        return [
            HumorTipo(1, 'img/icon/feliz.png'),
            HumorTipo(2, 'img/icon/triste.png')
        ]


def get_humor_map():
    """Retorna um dicionário mapeando o ID do HumorTipo para o caminho do ícone."""
    try:
        # Tenta usar o modelo HumorTipo mockado
        humor_map = {
            humor.pk: humor.icone
            for humor in HumorTipo.objects_all()
        }
    except Exception:
        humor_map = {1: 'img/icon/feliz.png', 2: 'img/icon/triste.png'}
        
    return humor_map


def _get_humor_cor_classe(estado):
    """Mapeia o estado do HumorTipo para uma classe CSS para colorir (relatórios)."""
    # Mapeamento do nome do estado (string) para a classe CSS (para estilização)
    mapping = {
        'Feliz': 'img/icon/feliz.png',
        'Calmo': 'img/icon/calmo.png', 
        'Ansioso': 'img/icon/ansioso.png',
        'Triste': 'img/icon/triste.png',
        'Irritado': 'img/icon/raiva.png',     
    }
    return mapping.get(estado, 'bg-light')


# -------------------------------------------------------------------
# LÓGICA AUXILIAR PARA HÁBITOS (Mantida do original)
# -------------------------------------------------------------------

def _get_checked_days_for_last_7_days(habito_obj):
    """
    Gera um mapa de conclusão (True/False) para os últimos 7 dias.
    A chave é a data no formato 'YYYY-MM-DD'.
    (Em um projeto real, esta função usaria o modelo StatusDiario.)
    """
    
    today = timezone.localdate()
    seven_days_ago = today - timedelta(days=6)
    
    # MOCK: Simula a busca de conclusões
    completions = []
    # Simulando 3 dias de conclusão para um hábito com ID 1
    class HabitoMockID:
         id = 1
    if habito_obj.id == 1: 
        completions = [today, today - timedelta(days=1), today - timedelta(days=3)]
    
    result_map = {
        (today - timedelta(days=i)).strftime('%Y-%m-%d'): False
        for i in range(7)
    }
    
    for c_date in completions:
        if seven_days_ago <= c_date <= today:
            result_map[c_date.strftime('%Y-%m-%d')] = True
            
    return result_map


# -------------------------------------------------------------------
# MOCKS DE CLASSES E FUNÇÕES (Necessário para Views de Exportação)
# -------------------------------------------------------------------

# Mocks para Hábitos
class Habito:
    def __init__(self, id, nome):
        self.id= id
        self.nome = nome

class AcompanhamentoHabito:
    def __init__(self, habito_id, data, concluido):
        self.habito_id = habito_id
        self.data = data
        self.concluido = concluido

def get_habitos_e_acompanhamento(user, data_inicio, data_fim):
    """
    MOCK: Simula a busca de dados do ORM para o relatório de Hábitos.
    """
    
    # 1. Busca todos os hábitos do usuário
    habito_list = [
        Habito(1, "Beber 2L de água"),
        Habito(2, "Meditar 10 minutos"),
        Habito(3, "Ler 20 páginas"),
    ]

    # 2. MOCKUP DE ACOMPANHAMENTO no período (Datas: Hoje, Hoje - 1, Hoje - 2)
    hoje = timezone.localdate()
    yesterday = hoje - timedelta(days=1)
    day_before = hoje - timedelta(days=2)
    
    acompanhamentos = [
        AcompanhamentoHabito(1, hoje, True), # Água: Concluído hoje
        AcompanhamentoHabito(1, yesterday, True), # Água: Concluído ontem
        AcompanhamentoHabito(2, hoje, False), # Meditar: Não Concluído hoje
        AcompanhamentoHabito(2, day_before, True), # Meditar: Concluído 2 dias atrás
        AcompanhamentoHabito(3, hoje, True), # Leitura: Concluído hoje
    ]
    
    # 3. Estrutura o resultado
    habitos_processados = []
    
    for habito in habito_list:
        acompanhamento_map = {} # {data: status (True/False)}
        
        for ac in acompanhamentos:
            if ac.habito_id == habito.id and data_inicio <= ac.data <= data_fim:
                acompanhamento_map[ac.data] = ac.concluido

        habitos_processados.append({
            'id': habito.id,
            'nome': habito.nome,
            'acompanhamento': acompanhamento_map
        })
        
    return habitos_processados

# Mocks para Humor
class HumorMock:
    """Modelo Mockup de Humor"""
    def __init__(self, id, data, nota, descricao, fatores, data_registro):
        self.idhumor = id
        self.data = data
        self.notahumor = nota
        self.descricaohumor = descricao
        self.fatores = fatores
        self.data_registro = data_registro

class HumorManager:
    """Gerenciador Mockup para simular consultas ao ORM de Humor."""
    def filter(self, usuario, data__gte, data__lte):
        """Simula a busca de registros de humor dentro do intervalo."""
        # Gera dados mockados (usando o modelo mock)
        hoje = timezone.localdate()
        yesterday = hoje - timedelta(days=1)
        
        registros_mock = [
            HumorMock(101, hoje, Decimal('4.5'), "Dia muito produtivo e feliz", "Trabalho Concluído, Exercício Físico", timezone.now() - timedelta(hours=2)),
            HumorMock(102, yesterday, Decimal('2.0'), "Manhã estressante com trânsito", "Trânsito, Pouco Sono", timezone.now() - timedelta(days=1, hours=8)),
            HumorMock(103, hoje - timedelta(days=5), Decimal('3.8'), "Neutro, mas com boa refeição.", "Boa Alimentação", timezone.now() - timedelta(days=5, hours=10)),
        ]
        
        # Filtra os mocks para simular o comportamento do ORM
        return [
            r for r in registros_mock if data__gte <= r.data <= data__lte
        ]

# Instância do gerenciador mock de Humor
Humor_mock = HumorManager()
