# app_LyfeSync/urls.py

from django.urls import path, include
# Importa todas as views exportadas via __init__.py
# A partir de agora, use 'views.' seguido do nome da função (ex: views.home)
from .views import (
    home, sobre_nos, contatos,home_lyfesync, habito, registrar_habito, 
    alterar_habito, toggle_habito_day, delete_habit, get_habit_data,
    autocuidado, humor, registrar_humor, alterar_humor, load_humor_by_date,
    gratidao, registrar_gratidao, alterar_gratidao,
    afirmacao, registrar_afirmacao, alterar_afirmacao,
    relatorios, relatorio_habito, relatorio_humor, relatorio_gratidao, relatorio_afirmacao,
    conta, configuracoes_conta, registrar_dica
)
#from django.contrib.auth import views as auth_views

urlpatterns = [
    # -------------------------------------------------------------------
    # PÁGINAS PÚBLICAS E AUTENTICAÇÃO
    # -------------------------------------------------------------------
    path('', home, name='home'),
    path('sobre-nos/', sobre_nos, name='sobre_nos'),
    path('contatos/', contatos, name='contatos'),
    #path('cadastro/', cadastro, name='cadastro'),
    
    # Views customizadas de Login/Logout - REMOVIDO: Views customizadas de Login/Logout para evitar conflito com 'allauth'
    #path('login/', login_view, name='login'),
    #path('logout/', logout_view, name='logout'), 
    
    # Dashboard (Página Inicial Logada)
    path('home-lyfesync/', home_lyfesync, name='homeLyfesync'),
    
    # -------------------------------------------------------------------
    # HÁBITOS
    # -------------------------------------------------------------------
    path('habito/', habito, name='habito'),
    path('habitos/registrar/', registrar_habito, name='registrar_habito'),
    path('habitos/alterar/<int:habito_id>/', alterar_habito, name='alterar_habito'), 
    path('habitos/get-data/<int:habit_id>/', get_habit_data, name='get_habit_data'), 
    path('habitos/toggle_day/<int:habit_id>/<str:day>/', toggle_habito_day, name='toggle_habit_day'),
    path('habitos/excluir/<int:habit_id>/', delete_habit, name='delete_habit'),

    # -------------------------------------------------------------------
    # AUTOCUIDADO (Página principal e sub-módulos)
    # -------------------------------------------------------------------
    path('autocuidado/', autocuidado, name='autocuidado'),
    
    # HUMOR
    path('humor/', humor, name='humor'),
    path('humor/registrar/', registrar_humor, name='registrarHumor'),
    path('api/humor/load/', load_humor_by_date, name='load_humor_by_date'),
    path('humor/alterar/<int:humor_id>/', alterar_humor, name='alterarHumor'),
    
    # GRATIDÃO
    path('gratidao/', gratidao, name='gratidao'),
    path('gratidao/registrar/', registrar_gratidao, name='registrar_gratidao'),
    path('gratidao/alterar/<int:gratidao_id>/', alterar_gratidao, name='alterar_gratidao'), 
    
    # AFIRMAÇÃO
    path('afirmacao/', afirmacao, name='afirmacao'),
    path('afirmacao/registrar/', registrar_afirmacao, name='registrar_afirmacao'),
    path('afirmacao/alterar/<int:afirmacao_id>/', alterar_afirmacao, name='alterar_afirmacao'), 

    # -------------------------------------------------------------------
    # RELATÓRIOS
    # -------------------------------------------------------------------
    path('relatorios/', relatorios, name='relatorios'),
    path('relatorios/habito/', relatorio_habito, name='relatorio_habito'),
    path('relatorios/humor/', relatorio_humor, name='relatorio_humor'),
    path('relatorios/gratidao/', relatorio_gratidao, name='relatorio_gratidao'),
    path('relatorios/afirmacao/', relatorio_afirmacao, name='relatorio_afirmacao'),
    
    # -------------------------------------------------------------------
    # CONTA E ADMIN
    # -------------------------------------------------------------------
    path('conta/', conta, name='conta'),
    path('configuracoes/', configuracoes_conta, name='configuracoes_conta'),
    path('dicas/registrar/', registrar_dica, name='registrar_dica'),
    
    # -------------------------------------------------------------------
    # INTEGRAÇÃO COM ALLAUTH (Se aplicável)
    # -------------------------------------------------------------------
    path('accounts/', include('allauth.urls')),
]