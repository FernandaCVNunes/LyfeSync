# app_LyfeSync/views/_aux.logic.py
from datetime import date, timedelta, datetime
from django.utils import timezone
from decimal import Decimal
import calendar
from django.db import models # Necessário para o Q object no mock de Habito

# Importa os Models reais apenas para fins de tipagem e mapeamento,
# mas as classes mockadas são usadas para simular o comportamento do ORM.
from ..models import StatusDiario, HumorTipo 

# -------------------------------------------------------------------
# LÓGICA AUXILIAR PRINCIPAL
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

# -------------------------------------------------------------------
# LÓGICA AUXILIAR PARA HUMOR (Mantida do original)
# -------------------------------------------------------------------

def get_humor_map():
    """Retorna um dicionário mapeando o nome do humor (estado) para o caminho do ícone.
    (Em um projeto real, esta função consultaria o modelo HumorTipo.)
    """
    # MOCK: Simula a busca de tipos de humor
    return {
        'Excelente': '/static/icons/excelente.png',
        'Bom': '/static/icons/bom.png',
        'Neutro': '/static/icons/neutro.png',
        'Ruim': '/static/icons/ruim.png',
        'Péssimo': '/static/icons/pessimo.png',
    }

def _get_humor_cor_classe(estado):
    """Mapeia o estado do HumorTipo para uma classe CSS para colorir (relatórios)."""
    # Mapeamento do nome do estado (string) para a classe CSS (para estilização)
    mapping = {
        'Excelente': 'humor-excelente',
        'Bom': 'humor-bom',
        'Neutro': 'humor-neutro',
        'Ruim': 'humor-ruim',
        'Péssimo': 'humor-pessimo',
        # Adicione outros mapeamentos conforme seus estados de humor em HumorTipo
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
    if habito_obj.idhabito == 1: 
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
        self.idhabito = id
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
            if ac.habito_id == habito.idhabito and data_inicio <= ac.data <= data_fim:
                acompanhamento_map[ac.data] = ac.concluido

        habitos_processados.append({
            'id': habito.idhabito,
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