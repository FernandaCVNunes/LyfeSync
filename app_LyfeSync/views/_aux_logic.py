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
        'Feliz': 'img/icon/feliz.png',
        'Calmo': 'img/icon/calmo.png',
        'Ansioso': 'img/icon/ansioso.png',
        'Triste': 'img/icon/triste.png',
        'Irritado': 'img/icon/raiva.png',
    }

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

def extract_dica_info(dica_raw: str) -> dict:
    """
    Extrai informações estruturadas de uma string de "dica" em formato raw (bruto).

    Esta função assume que a string de dica está formatada da seguinte forma:
    "<Título ou Categoria>:<Conteúdo da Dica>"
    
    Exemplo: "Saúde:Beba pelo menos 2 litros de água por dia."

    Args:
        dica_raw (str): A string de dica bruta a ser processada.

    Returns:
        dict: Um dicionário com as chaves 'categoria' e 'conteudo'.
    """
    try:
        # Tenta dividir a string no primeiro ':' encontrado.
        # Isto é comum em logs ou dados semi-estruturados.
        if ':' in dica_raw:
            categoria, conteudo = dica_raw.split(':', 1)
            return {
                "categoria": categoria.strip(),
                "conteudo": conteudo.strip()
            }
        else:
            # Se não houver delimitador, assume-se que toda a string é o conteúdo
            return {
                "categoria": "Geral",
                "conteudo": dica_raw.strip()
            }
    except Exception as e:
        print(f"Erro ao extrair informação da dica '{dica_raw}': {e}")
        return {
            "categoria": "Erro",
            "conteudo": dica_raw
        }

def rebuild_descricaohumor(descricao: str, humor: str) -> str:
    """
    Reconstrói e formata uma string final combinando uma descrição de evento/situação
    com um rótulo de humor (sentiment) associado.

    O objetivo é criar uma saída legível e padronizada.

    Args:
        descricao (str): A descrição principal do evento ou situação.
        humor (str): O rótulo de humor ou sentimento associado (e.g., "Alegre", "Triste", "Sarcástico").

    Returns:
        str: A string formatada final.
    """
    # Garante que o rótulo de humor esteja em maiúsculas e entre parênteses retos
    humor_formatado = f"[{humor.upper()}]"
    
    # Combina a descrição e o humor formatado.
    # Exemplo: "O dia está ótimo, o sol brilha" [ALEGRE]
    return f"{descricao.strip()} {humor_formatado}"

# --- Exemplos de Uso ---
if __name__ == '__main__':
    print("--- Teste de extract_dica_info ---")
    dica1 = "Produtividade:Use a técnica Pomodoro para manter o foco."
    dica2 = "Lazer:Tire um tempo para caminhar ao ar livre."
    dica3 = "Apenas uma frase de dica sem categoria."

    info1 = extract_dica_info(dica1)
    info2 = extract_dica_info(dica2)
    info3 = extract_dica_info(dica3)

    print(f"Dica 1 (Original: '{dica1}'): {info1}")
    print(f"Dica 2 (Original: '{dica2}'): {info2}")
    print(f"Dica 3 (Original: '{dica3}'): {info3}")
    
    print("\n--- Teste de rebuild_descricaohumor ---")
    desc1 = "Recebi a notícia de que o projeto foi aprovado."
    humor1 = "alegre"
    
    desc2 = "Demorou mais tempo do que o esperado para terminar esta tarefa."
    humor2 = "frustrado"

    resultado1 = rebuild_descricaohumor(desc1, humor1)
    resultado2 = rebuild_descricaohumor(desc2, humor2)

    print(f"Resultado 1: {resultado1}")
    print(f"Resultado 2: {resultado2}")