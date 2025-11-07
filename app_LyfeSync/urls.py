from django.urls import path, include
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    # Páginas Públicas
    path('', views.home, name='home'),
    path('sobre-nos/', views.sobre_nos, name='sobre_nos'),
    path('contatos/', views.contatos, name='contatos'),
    path('cadastro/', views.cadastro, name='cadastro'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    
    # Dashboard (Página Inicial Logada)
    # A URL que deu erro foi /home-lyfesync/, mas a view se chama home_lyfesync.
    # O nome interno usado no template deve ser 'homeLyfesync'.
    path('home-lyfesync/', views.home_lyfesync, name='homeLyfesync'),
    
    # HÁBITOS
    path('habito/', views.habito, name='habito'),
    path('habitos/registrar/', views.registrar_habito, name='registrar_habito'),
    path('habitos/alterar/<int:habito_id>/', views.alterar_habito, name='alterar_habito'), # Adicionado <int:habito_id>
    path('habitos/toggle_day/<int:habit_id>/<str:day>/', views.toggle_habito_day, name='toggle_habit_day'),
    path('habitos/delete/<int:habit_id>/', views.delete_habit, name='delete_habit'),

    # AUTOCUIDADO (Página principal de Afirmação, Gratidão e Humor)
    path('autocuidado/', views.autocuidado, name='autocuidado'),
    
    # HUMOR
    path('humor/', views.humor, name='humor'),
    # Esta é a URL principal referenciada no sidebar.
    path('humor/registrar/', views.registrar_humor, name='registrarHumor'),
    path('api/humor/load/', views.load_humor_by_date, name='load_humor_by_date'),
    path('humor/alterar/<int:humor_id>/', views.alterar_humor, name='alterarHumor'),
    
    # GRATIDÃO
    path('gratidao/', views.gratidao, name='gratidao'),
    path('gratidao/registrar/', views.registrar_gratidao, name='registrar_gratidao'),
    path('gratidao/alterar/', views.alterar_gratidao, name='alterar_gratidao'), # Adapte esta URL se precisar de um ID
    
    # AFIRMAÇÃO
    path('afirmacao/', views.afirmacao, name='afirmacao'),
    path('afirmacao/registrar/', views.registrar_afirmacao, name='registrar_afirmacao'),
    path('afirmacao/alterar/', views.alterar_afirmacao, name='alterar_afirmacao'), # Adapte esta URL se precisar de um ID

    # RELATÓRIOS
    path('relatorios/', views.relatorios, name='relatorios'),
    path('relatorios/habito/', views.relatorio_habito, name='relatorio_habito'),
    path('relatorios/humor/', views.relatorio_humor, name='relatorio_humor'),
    path('relatorios/gratidao/', views.relatorio_gratidao, name='relatorio_gratidao'),
    path('relatorios/afirmacao/', views.relatorio_afirmacao, name='relatorio_afirmacao'),
    
    # CONTA E ADMIN
    path('conta/', views.conta, name='conta'),
    path('configuracoes/', views.configuracoes_conta, name='configuracoes_conta'),
    path('dicas/registrar/', views.registrar_dica, name='registrar_dica'),
    
    # URLs do Allauth
    path('accounts/', include('allauth.urls')),
]