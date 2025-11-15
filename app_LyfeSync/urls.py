# app_LyfeSync/urls.py

from django.urls import path, include

from .views import (
    # Views Públicas
    home, sobre_nos, contatos,
    
    # Views de Dashboard
    home_lyfesync,
    
    # Views de Configuração/Conta
    conta, configuracoes_conta, excluir_conta,
    
    # Views de Hábitos
    habito, registrar_habito, alterar_habito, toggle_habito_day, 
    delete_habit, get_habit_data,
    
    # Views de Autocuidado (CRUD)
    autocuidado,
    
    # Humor
    humor, registrar_humor, alterar_humor, load_humor_by_date, 
    delete_humor,
    
    # Gratidão
    gratidao, registrar_gratidao, alterar_gratidao, delete_gratidao,
    
    # Afirmação
    afirmacao, registrar_afirmacao, alterar_afirmacao, delete_afirmacao,
    
    # Views de Dicas (Staff/Admin)
    registrar_dica, admin_registrar_dica, alterar_dica, excluir_dica,
    
    # Views de Relatório
    relatorios, relatorio, _get_humor_cor_classe,
    relatorio_habito, relatorio_humor, relatorio_gratidao, relatorio_afirmacao,
    
    # Views de Exportação
    exportar_habito_csv, exportar_habito_pdf,
    exportar_gratidao_csv, exportar_gratidao_pdf,
    exportar_afirmacao_csv, exportar_afirmacao_pdf, 
    exportar_humor_csv, exportar_humor_pdf, 
)

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
    path('humor/delete/<int:humor_id>/', delete_humor, name='delete_humor'),
    
    # GRATIDÃO
    path('gratidao/', gratidao, name='gratidao'),
    path('gratidao/registrar/', registrar_gratidao, name='registrar_gratidao'),
    path('gratidao/alterar/<int:gratidao_id>/', alterar_gratidao, name='alterar_gratidao'),
    path('gratidao/excluir/<int:gratidao_id>/', delete_gratidao, name='delete_gratidao'), 
    
    # AFIRMAÇÃO
    path('afirmacao/', afirmacao, name='afirmacao'),
    path('afirmacao/registrar/', registrar_afirmacao, name='registrar_afirmacao'),
    path('afirmacao/alterar/<int:afirmacao_id>/', alterar_afirmacao, name='alterar_afirmacao'),
    path('afirmacao/excluir/<int:afirmacao_id>/', delete_afirmacao, name='delete_afirmacao'),  

    # -------------------------------------------------------------------
    # RELATÓRIOS
    # -------------------------------------------------------------------
    path('relatorios/', relatorios, name='relatorios'),
    path('relatorios/habito/', relatorio_habito, name='relatorio_habito'),
    path('relatorios/humor/', relatorio_humor, name='relatorio_humor'),
    path('relatorios/gratidao/', relatorio_gratidao, name='relatorio_gratidao'),
    path('relatorios/afirmacao/', relatorio_afirmacao, name='relatorio_afirmacao'),
    #Exportar relatórios
    path('relatorio/gratidao/exportar/csv/', exportar_gratidao_csv, name='exportar_gratidao_csv'),
    path('relatorio/gratidao/exportar/pdf/', exportar_gratidao_pdf, name='exportar_gratidao_pdf'),
    path('relatorio/afirmacao/exportar/csv/', exportar_afirmacao_csv, name='exportar_afirmacao_csv'),
    path('relatorio/afirmacao/exportar/pdf/', exportar_afirmacao_pdf, name='exportar_afirmacao_pdf'),
    path('relatorio/habito/exportar/csv/', exportar_habito_csv, name='exportar_habito_csv'),
    path('relatorio/habito/exportar/pdf/', exportar_habito_pdf, name='exportar_habito_pdf'),
    path('relatorio/humor/exportar/csv/', exportar_humor_csv, name='exportar_humor_csv'),
    path('relatorio/humor/exportar/pdf/', exportar_humor_pdf, name='exportar_humor_pdf'),

    # -------------------------------------------------------------------
    # CONTA E ADMIN
    # -------------------------------------------------------------------
    path('conta/', conta, name='conta'),
    path('configuracoes/', configuracoes_conta, name='configuracoes_conta'),
    path('configuracoes/excluir-conta/', excluir_conta, name='excluir_conta'),

    path('dicas/registrar/', registrar_dica, name='registrar_dica'),
    path('dicas/alterar/<int:dica_id>/', alterar_dica, name='alterar_dica'), 
    path('dicas/excluir/<int:dica_id>/', excluir_dica, name='excluir_dica'),
    
    # -------------------------------------------------------------------
    # INTEGRAÇÃO COM ALLAUTH (Se aplicável)
    # -------------------------------------------------------------------
    path('accounts/', include('allauth.urls')),
]