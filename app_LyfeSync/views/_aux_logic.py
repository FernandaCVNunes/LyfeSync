# app_LyfeSync/views/_aux.logic.py
from datetime import date
from ..models import StatusDiario

# -------------------------------------------------------------------
# LÓGICA AUXILIAR PARA HUMOR
# -------------------------------------------------------------------

def get_humor_map():
    """Define o mapeamento dos códigos de humor (salvos no BD) para os caminhos das imagens estáticas."""
    # Caminhos relativos à sua pasta static (ex: static/img/icon/)
    return {
        'Feliz': 'img/icon/feliz.png',
        'Calmo': 'img/icon/calmo.png',
        'Ansioso': 'img/icon/ansioso.png',
        'Triste': 'img/icon/triste.png',
        'Irritado': 'img/icon/raiva.png',
    }


# -------------------------------------------------------------------
# LÓGICA AUXILIAR PARA HÁBITOS
# -------------------------------------------------------------------

def _get_checked_days_for_current_month(habito_obj):
    """Busca os dias em que o hábito foi concluído no mês atual."""
    month = date.today().month
    year = date.today().year
    
    # Consulta todas as conclusões para o hábito no mês e ano atuais
    # ASSUMIDO: O campo de data em StatusDiario é 'data_conclusao'
    completions = StatusDiario.objects.filter(
        habito=habito_obj, 
        data_conclusao__year=year, 
        data_conclusao__month=month
    )
    
    # Cria o dicionário de mapa: {dia_do_mês: True}
    checked_days = {c.data_conclusao.day: True for c in completions}
    return checked_days