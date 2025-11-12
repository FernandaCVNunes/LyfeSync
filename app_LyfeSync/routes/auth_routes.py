from django.urls import path

# NOTA: Assumimos que as funções de vista (views) de autenticação serão
# definidas num módulo chamado 'auth_views' dentro da nossa aplicação.
# Iremos substituir 'from ..views.auth_views import' pelos imports reais
# assim que as views forem criadas. Por agora, usamos placeholders funcionais.
from app_LyfeSync.views import user_login, user_logout, user_register, password_change

# A lista urlpatterns contém todas as rotas específicas para a autenticação.
urlpatterns = [
    # Rota para o ecrã de Login
    path('login/', user_login, name='login'),
    
    # Rota para o ecrã de Registo (Criação de Conta)
    path('register/', user_register, name='register'),
    
    # Rota para o ecrã de Alteração de Senha
    path('password_change/', password_change, name='password_change'),
    
    # Rota para o Logout (irá limpar a sessão e redirecionar)
    path('logout/', user_logout, name='logout'),
    
    # NOTA: O fluxo de 'password reset' (recuperação de senha) é tipicamente
    # mais complexo e pode utilizar as vistas embutidas do Django, mas as
    # rotas principais estão aqui definidas.
]
