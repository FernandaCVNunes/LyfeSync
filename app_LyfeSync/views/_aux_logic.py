# app_LyfeSync/views/_aux.logic.py
from datetime import date
from ..models import StatusDiario, HumorTipo # Adicionar HumorTipo aqui
from django.utils import timezone # Adicionar timezone para uso consistente

# -------------------------------------------------------------------
# LÓGICA AUXILIAR PARA HUMOR
# -------------------------------------------------------------------

def get_humor_map():
    """Retorna um dicionário mapeando o nome do humor (estado) para o caminho do ícone."""
    # Busca todos os tipos de humor disponíveis
    humor_tipos = HumorTipo.objects.all()
    # Cria o mapeamento: {'Estado do Humor': 'icone'}
    return {tipo.estado: tipo.icone for tipo in humor_tipos} 


# -------------------------------------------------------------------
# LÓGICA AUXILIAR PARA HÁBITOS
# -------------------------------------------------------------------

def _get_checked_days_for_current_month(habito_obj):
   """Busca os dias em que o hábito foi concluído no mês atual."""
   month = timezone.localdate().month
   year = timezone.localdate().year
   
   # CORREÇÃO CRÍTICA: O campo de data em StatusDiario é 'data', não 'data_conclusao'.
   completions = StatusDiario.objects.filter(
      habito=habito_obj, 
      data__year=year, 
      data__month=month,
      concluido=True # Adicionar filtro para garantir que só conta o que foi concluído
   )
   
   # CORREÇÃO: Usar o campo 'data' (do model)
   checked_days = {c.data.day: True for c in completions}
   return checked_days