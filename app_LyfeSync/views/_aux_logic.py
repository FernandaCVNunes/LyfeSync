# app_LyfeSync/views/_aux.logic.py
from datetime import date, timedelta
from ..models import StatusDiario, HumorTipo 
from django.utils import timezone 

# -------------------------------------------------------------------
# LÓGICA AUXILIAR PARA HUMOR
# -------------------------------------------------------------------

def get_humor_map():
    """Retorna um dicionário mapeando o nome do humor (estado) para o caminho do ícone."""
    humor_tipos = HumorTipo.objects.all()
    return {tipo.estado: tipo.icone for tipo in humor_tipos} 


# -------------------------------------------------------------------
# LÓGICA AUXILIAR PARA HÁBITOS
# -------------------------------------------------------------------

def _get_checked_days_for_last_7_days(habito_obj):
    """
    Gera um mapa de conclusão (True/False) para os últimos 7 dias.
    A chave é a data no formato 'YYYY-MM-DD'.
    """
    
    today = timezone.localdate()
    seven_days_ago = today - timedelta(days=6)
    
    # 1. Busca no BD apenas as conclusões dentro da janela de 7 dias
    completions = StatusDiario.objects.filter(
        habito=habito_obj, 
        data__gte=seven_days_ago, 
        data__lte=today, 
        concluido=True # Só precisamos dos dias que foram marcados como CONCLUÍDOS
    ).values_list('data', flat=True) # Retorna apenas a lista de datas concluídas

    # 2. Converte as datas concluídas para um Set para pesquisa rápida
    completed_dates_set = {d.strftime('%Y-%m-%d') for d in completions}
    
    # 3. Cria o mapa de status para os 7 dias
    checked_days_map = {}
    for i in range(7):
        current_date = today - timedelta(days=6 - i)
        date_key = current_date.strftime('%Y-%m-%d') 
        # O valor é True se a data estiver no set de datas concluídas
        checked_days_map[date_key] = date_key in completed_dates_set

    return checked_days_map