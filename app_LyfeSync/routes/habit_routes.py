from django.urls import path

# NOTA: As vistas (views) serão definidas em 'habit_views.py'.
from app_LyfeSync.views import (
    habit_list,          # Ver todos os hábitos
    habit_create,        # Criar um novo hábito
    habit_detail,        # Ver detalhes de um hábito específico
    habit_update,        # Editar um hábito existente
    habit_delete,        # Eliminar um hábito
    habit_track_toggle,  # Marcar/desmarcar um hábito como concluído
)

# A lista urlpatterns contém todas as rotas específicas para a gestão de Hábitos.
urlpatterns = [
    # Rota principal de Hábitos (lista e visualização geral)
    path('', habit_list, name='habit_list'),
    
    # Rota para adicionar um novo hábito
    path('create/', habit_create, name='habit_create'),
    
    # Rotas para interagir com um hábito específico (usando o ID do hábito)
    path('<int:habit_id>/', habit_detail, name='habit_detail'),
    path('<int:habit_id>/update/', habit_update, name='habit_update'),
    path('<int:habit_id>/delete/', habit_delete, name='habit_delete'),
    
    # Rota para marcar/desmarcar o hábito como concluído para o dia atual ou especificado
    # O método HTTP (POST/GET) e a lógica de data serão tratados na vista.
    path('<int:habit_id>/track/', habit_track_toggle, name='habit_track_toggle'),
]