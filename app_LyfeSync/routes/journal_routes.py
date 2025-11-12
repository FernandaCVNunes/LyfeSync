from django.urls import path

# NOTA: As vistas (views) serão definidas em 'journal_views.py'.
from app_LyfeSync.views import (
    journal_list,      # Ver todas as entradas ou filtrar por data
    journal_create,    # Criar uma nova entrada de diário
    journal_detail,    # Ver o conteúdo de uma entrada específica
    journal_update,    # Editar uma entrada existente
    journal_delete,    # Eliminar uma entrada
)

# A lista urlpatterns contém todas as rotas específicas para a gestão do Diário.
urlpatterns = [
    # Rota principal do Diário (lista de entradas, com potencial filtro por data)
    path('', journal_list, name='journal_list'),
    
    # Rota para iniciar/criar uma nova entrada (geralmente para o dia atual)
    path('create/', journal_create, name='journal_create'),
    
    # Rotas para interagir com uma entrada específica (usando o ID da entrada)
    # Assume-se que o 'entry_id' será o identificador da entrada no modelo JournalEntry.
    path('<int:entry_id>/', journal_detail, name='journal_detail'),
    path('<int:entry_id>/update/', journal_update, name='journal_update'),
    path('<int:entry_id>/delete/', journal_delete, name='journal_delete'),
    
    # Podemos adicionar uma rota para visualizar entradas por data se necessário:
    # path('<int:year>/<int:month>/<int:day>/', journal_detail_by_date, name='journal_detail_by_date'),
]