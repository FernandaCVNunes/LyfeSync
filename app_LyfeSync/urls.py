# app_LyfeSync/urls.py

from django.urls import path, include
# Importa o módulo 'views' que é o seu arquivo 'views/__init__.py'
from .views import views 
from django.contrib.auth import views as auth_views

urlpatterns = [
    # -------------------------------------------------------------------
    # PÁGINAS PÚBLICAS E AUTENTICAÇÃO
    # -------------------------------------------------------------------
    path('', views.home, name='home'),
    path('sobre-nos/', views.sobre_nos, name='sobre_nos'),
    path('contatos/', views.contatos, name='contatos'),
    path('cadastro/', views.cadastro, name='cadastro'),
    
    # As URLs de Login/Logout do Django (se você não estiver usando allauth para elas)
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'), 
    
    # Dashboard (Página Inicial Logada)
    path('home-lyfesync/', views.home_lyfesync, name='homeLyfesync'),
    
    # -------------------------------------------------------------------
    # HÁBITOS
    # -------------------------------------------------------------------
    path('habito/', views.habito, name='habito'),
    path('habitos/registrar/', views.registrar_habito, name='registrar_habito'),
    path('habitos/alterar/<int:habito_id>/', views.alterar_habito, name='alterar_habito'), 
    path('habitos/toggle_day/<int:habit_id>/<str:day>/', views.toggle_habito_day, name='toggle_habit_day'),
    path('habitos/delete/<int:habit_id>/', views.delete_habit, name='delete_habit'),

    # -------------------------------------------------------------------
    # AUTOCUIDADO (Página principal e sub-módulos)
    # -------------------------------------------------------------------
    path('autocuidado/', views.autocuidado, name='autocuidado'),
    
    # HUMOR
    path('humor/', views.humor, name='humor'),
    path('humor/registrar/', views.registrar_humor, name='registrarHumor'),
    path('api/humor/load/', views.load_humor_by_date, name='load_humor_by_date'),
    path('humor/alterar/<int:humor_id>/', views.alterar_humor, name='alterarHumor'),
    
    # GRATIDÃO
    path('gratidao/', views.gratidao, name='gratidao'),
    path('gratidao/registrar/', views.registrar_gratidao, name='registrar_gratidao'),
    # Atenção: 'alterar_gratidao' provavelmente precisa de um ID do objeto
    path('gratidao/alterar/<int:gratidao_id>/', views.alterar_gratidao, name='alterar_gratidao'), 
    
    # AFIRMAÇÃO
    path('afirmacao/', views.afirmacao, name='afirmacao'),
    path('afirmacao/registrar/', views.registrar_afirmacao, name='registrar_afirmacao'),
    # Atenção: 'alterar_afirmacao' provavelmente precisa de um ID do objeto
    path('afirmacao/alterar/<int:afirmacao_id>/', views.alterar_afirmacao, name='alterar_afirmacao'), 

    # -------------------------------------------------------------------
    # RELATÓRIOS
    # -------------------------------------------------------------------
    path('relatorios/', views.relatorios, name='relatorios'),
    path('relatorios/habito/', views.relatorio_habito, name='relatorio_habito'),
    path('relatorios/humor/', views.relatorio_humor, name='relatorio_humor'),
    path('relatorios/gratidao/', views.relatorio_gratidao, name='relatorio_gratidao'),
    path('relatorios/afirmacao/', views.relatorio_afirmacao, name='relatorio_afirmacao'),
    
    # -------------------------------------------------------------------
    # CONTA E ADMIN
    # -------------------------------------------------------------------
    path('conta/', views.conta, name='conta'),
    path('configuracoes/', views.configuracoes_conta, name='configuracoes_conta'),
    path('dicas/registrar/', views.registrar_dica, name='registrar_dica'),
    
    # -------------------------------------------------------------------
    # INTEGRAÇÃO COM ALLAUTH
    # -------------------------------------------------------------------
    # Mantenha esta linha se estiver usando o django-allauth.
    path('accounts/', include('allauth.urls')),
]