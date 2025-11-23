# app_LyfeSync/views/_aux.logic.py
from datetime import date, timedelta, datetime
from django.utils import timezone
from decimal import Decimal
import calendar
import re
from django.db import models 
from ..models import StatusDiario, HumorTipo 
from datetime import date, timedelta, datetime
from django.utils import timezone
from decimal import Decimal
import calendar
import re
from django.db import models 

# -------------------------------------------------------------------
# LÓGICA AUXILIAR PRINCIPAL
# -------------------------------------------------------------------

# VARIÁVEL DE REGEX CORRIGIDA:
# Agora captura o ID (Grupo 1) e o restante da descrição do usuário (Grupo 2)
# ^: Início da string | \s*: Captura zero ou mais espaços após a tag
DICA_DELIMITADOR_REGEX = r'^\[DICA ID:(\d+)\]\s*(.*)$'

# Função para extrair a informação da dica do campo descricaohumor
def extract_dica_info(descricaohumor):
    """
    Tenta extrair o ID da dica ([DICA ID:X]) e retorna a descrição limpa do usuário.
    
    Args:
        descricaohumor (str): O campo 'descricaohumor' do modelo Humor.
        
    Returns:
        tuple: (dica_id_salva: int|None, descricao_usuario_original: str)
    """
    if not descricaohumor:
        return None, ""
        
    descricaohumor = descricaohumor.strip()
    # Usa o regex robusto para casar o padrão do início ao fim
    match = re.match(DICA_DELIMITADOR_REGEX, descricaohumor)
    
    if match:
        dica_id_salva = int(match.group(1)) # Grupo 1: O ID da dica (X em [DICA ID:X])
        # Grupo 2: O restante da descrição (já limpo pelo regex)
        descricao_usuario_original = match.group(2).strip()
    else:
        dica_id_salva = None
        # Se não houver a tag, toda a string é a descrição original do usuário
        descricao_usuario_original = descricaohumor
        
    return dica_id_salva, descricao_usuario_original

def rebuild_descricaohumor(dica_id, descricao_usuario):
    """
    Reconstrói o campo 'descricaohumor' adicionando a tag [DICA ID:X] de volta.
    
    Args:
        dica_id (int|None): O ID da dica a ser persistida.
        descricao_usuario (str): A descrição fornecida pelo usuário.
        
    Returns:
        str: O novo campo 'descricaohumor' formatado.
    """
    descricao_usuario = descricao_usuario.strip()
    if dica_id:
        # Garante o formato: [DICA ID:X] <Descrição do Usuário>
        return f"[DICA ID:{dica_id}] {descricao_usuario}"
    return descricao_usuario

# -------------------------------------------------------------------
# LÓGICA AUXILIAR DIVERSA (Mantida para evitar erros de dependência)
# -------------------------------------------------------------------

def _get_report_date_range(request, hoje, default_periodo=None):
    """
    Calcula o intervalo de datas (inicio e fim) com base nos parâmetros GET.
    """
    
    # 1. Definir o período (PRIORIZE ESTA LÓGICA DE DEFINIÇÃO DO PERÍODO)
    if default_periodo in ['mensal', 'semanal', 'anual']:
        periodo = default_periodo
    else:
        periodo = request.GET.get('periodo', 'mensal') 

    # 2. Obter mês e ano para referência
    try:
        mes_param = int(request.GET.get('mes', hoje.month))
    except (ValueError, TypeError):
        mes_param = hoje.month
        
    try:
        ano_param = int(request.GET.get('ano', hoje.year))
    except (ValueError, TypeError):
        ano_param = hoje.year

    # 3. Criar a data de referência (CORREÇÃO DO ERRO 'utcoffset')
    try:
        data_referencia = date(year=ano_param, month=mes_param, day=1)
    except ValueError:
        data_referencia = hoje
    
    # 4. Cálculo do Intervalo (NÃO PODE HAVER RECURSÃO AQUI)
    if periodo == 'semanal':
        inicio_semana = hoje - timedelta(days=hoje.weekday())
        data_inicio = inicio_semana
        data_fim = inicio_semana + timedelta(days=6)
        
    elif periodo == 'anual':
        data_inicio = data_referencia.replace(month=1, day=1)
        data_fim = data_referencia.replace(month=12, day=31)
        
    # 'elif periodo == 'mensal': ou fallback
    else: 
        _, ultimo_dia_mes = calendar.monthrange(data_referencia.year, data_referencia.month)
        data_inicio = data_referencia.replace(day=1)
        data_fim = data_referencia.replace(day=ultimo_dia_mes)
        periodo = 'mensal'

    # 5. RETORNO FINAL
    return data_inicio, data_fim, data_referencia, periodo, mes_param, ano_param

def get_humor_map():
    """
    Retorna um dicionário mapeando o ID do HumorTipo para o caminho do ícone.
    Útil para preencher contextos de formulário e templates.
    """
    # MOCK: Substitua por HumorTipo.objects.all() no código real
    try:
        # Tenta usar o modelo HumorTipo, se estiver disponível
        from ..models import HumorTipo
        humor_map = {
            humor.pk: humor.icone
            for humor in HumorTipo.objects.all()
        }
    except Exception:
        # Fallback para um mapa mockado ou vazio
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