from django.urls import path

# NOTA: O dashboard é o ponto de entrada principal após o login.
# As vistas do dashboard serão definidas em 'dashboard_views.py'.
from app_LyfeSync.views import (
    dashboard_summary, 
    settings_view, 
    profile_view
)

# A lista urlpatterns contém todas as rotas específicas para a área principal do dashboard.
urlpatterns = [
    # Rota principal (ecrã de boas-vindas / resumo)
    # Por convenção, usamos a rota base (ex: /app/) após o login
    path('', dashboard_summary, name='dashboard_summary'),
    
    # Rota para a página de Definições/Configurações do utilizador
    path('settings/', settings_view, name='settings'),
    
    # Rota para o perfil do utilizador (informações e edição de dados pessoais)
    path('profile/', profile_view, name='profile'),
    
    # NOTA: As rotas para Diário, Hábitos e Tarefas serão definidas
    # nos seus próprios ficheiros de rotas dedicados (journal_routes, etc.)
]