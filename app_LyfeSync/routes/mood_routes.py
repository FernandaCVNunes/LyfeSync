from django.urls import path

# NOTA: As vistas (views) serão definidas em 'mood_views.py'.
from app_LyfeSync.views import (
    mood_list,      # Visualizar todas as entradas de humor, geralmente em formato de calendário/lista
    mood_create,    # Registar o humor do momento (ou de um dia específico)
    mood_detail,    # Ver detalhes de um registo de humor (opcional, ou usado para editar)
    mood_update,    # Editar um registo de humor existente
    mood_delete,    # Eliminar um registo de humor
)

# A lista urlpatterns contém todas as rotas específicas para a gestão do Humor.
urlpatterns = [
    # Rota principal do Humor (lista e visualização geral)
    path('', mood_list, name='mood_list'),
    
    # Rota para registar um novo estado de humor
    path('create/', mood_create, name='mood_create'),
    
    # Rotas para interagir com um registo específico (usando o ID do registo)
    # Assume-se que 'mood_id' será o identificador da entrada no modelo MoodEntry.
    path('<int:mood_id>/', mood_detail, name='mood_detail'),
    path('<int:mood_id>/update/', mood_update, name='mood_update'),
    path('<int:mood_id>/delete/', mood_delete, name='mood_delete'),
]