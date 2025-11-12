from django.urls import path

# NOTA: As vistas (views) serão definidas em 'task_views.py'.
from app_LyfeSync.views import (
    task_list,      # Visualizar todas as tarefas (lista de afazeres - To-Do List)
    task_create,    # Adicionar uma nova tarefa
    task_detail,    # Ver detalhes de uma tarefa específica
    task_update,    # Editar uma tarefa existente (p. ex., mudar prazo, descrição)
    task_complete,  # Marcar uma tarefa como concluída
    task_delete,    # Eliminar uma tarefa
)

# A lista urlpatterns contém todas as rotas específicas para a gestão de Tarefas.
urlpatterns = [
    # Rota principal de Tarefas (exibe a lista de afazeres pendentes)
    path('', task_list, name='task_list'),
    
    # Rota para adicionar uma nova tarefa
    path('create/', task_create, name='task_create'),
    
    # Rotas para interagir com uma tarefa específica (usando o ID da tarefa)
    # Assume-se que 'task_id' será o identificador da entrada no modelo Task.
    path('<int:task_id>/', task_detail, name='task_detail'),
    path('<int:task_id>/update/', task_update, name='task_update'),
    path('<int:task_id>/complete/', task_complete, name='task_complete'),
    path('<int:task_id>/delete/', task_delete, name='task_delete'),
]
