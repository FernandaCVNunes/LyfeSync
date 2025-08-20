from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('sobre-nos/', views.sobre_nos, name='sobre_nos'),
    path('contatos/', views.contatos, name='contatos'),
    path('login/', views.login, name='login'),
    path('home-lyfesync/', views.home_lyfesync, name='home_lyfesync'),
    path('habito/', views.habito, name='habito'),
    path('registrar-habito/', views.registrar_habito, name='registrar_habito'),
    path('alterar-habito/', views.alterar_habito, name='alterar_habito'),
    path('autocuidado/', views.autocuidado, name='autocuidado'),
    path('humor/', views.humor, name='humor'),
    path('gratidao/', views.gratidao, name='gratidao'),
    path('afirmacao/', views.afirmacao, name='afirmacao'),
    path('registrar-humor/', views.registrar_humor, name='registrar_humor'),
    path('alterar-humor/', views.alterar_humor, name='alterar_humor'),
    path('registrar-gratidao/', views.registrar_gratidao, name='registrar_gratidao'),
    path('alterar-gratidao/', views.alterar_gratidao, name='alterar_gratidao'),
    path('registrar-afirmacao/', views.registrar_afirmacao, name='registrar_afirmacao'),
    path('alterar-afirmacao/', views.alterar_afirmacao, name='alterar_afirmacao'),
    path('relatorios/', views.relatorios, name='relatorios'),
    path('relatorio-habito/', views.relatorio_habito, name='relatorio_habito'),
    path('relatorio-humor/', views.relatorio_humor, name='relatorio_humor'),
    path('relatorio-gratidao/', views.relatorio_gratidao, name='relatorio_gratidao'),
    path('relatorio-afirmacao/', views.relatorio_afirmacao, name='relatorio_afirmacao'),
]