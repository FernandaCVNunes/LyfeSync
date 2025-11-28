# app_LyfeSync/views/config_views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db import transaction
from django.contrib.auth import update_session_auth_hash
from django.urls import reverse
# Importações dos forms e models
from ..forms import UserUpdateForm, PerfilUsuarioForm, CustomPasswordChangeForm, ConsentimentoForm
from ..models import PerfilUsuario
from ._aux_logic import get_humor_map

# -------------------------------------------------------------------
#       Configurações de Dicas
# -------------------------------------------------------------------

# Função de teste para verificar se o usuário é superusuário (Admin)
def is_superuser(user):
    """Retorna True se o usuário for um superusuário ativo."""
    return user.is_active and user.is_superuser

# -------------------------------------------------------------------
#       Conta
# -------------------------------------------------------------------

@login_required( login_url='account_login')
def conta(request): 
    """Esta view é um atalho que redireciona para a view principal de configuração de conta."""
    return redirect('configuracoes_conta')

@login_required( login_url='account_login')
def configuracoes_conta(request):
   """Permite ao usuário alterar seus dados, dados de perfil e senha."""
   
   try:
      perfil_instance = request.user.perfil 
   except PerfilUsuario.DoesNotExist: 
      perfil_instance = PerfilUsuario(user=request.user)
   
   is_admin = request.user.is_superuser
    
    # --- 1. Inicializa todos os formulários antes do POST ---
   user_form = UserUpdateForm(instance=request.user)
   perfil_form = PerfilUsuarioForm(instance=perfil_instance)
   password_form = CustomPasswordChangeForm(user=request.user)
   consent_form = ConsentimentoForm()

   if request.method == 'POST':
      # Verifica qual formulário foi enviado usando o 'name' do botão submit
      
      if 'update_perfil' in request.POST:
         # Processamento de Perfil
         user_form = UserUpdateForm(request.POST, instance=request.user)
         perfil_form = PerfilUsuarioForm(request.POST, instance=perfil_instance)
         
         with transaction.atomic():
            forms_valid = True

            if user_form.is_valid():
               user_form.save()
            else:
               forms_valid = False
            
            if perfil_form.is_valid():
               perfil_obj = perfil_form.save(commit=False)
               perfil_obj.user = request.user 
               perfil_obj.save() 
            else:
               forms_valid = False 

            if forms_valid:
               messages.success(request, 'Suas configurações de perfil foram atualizadas com sucesso!')
               return redirect('configuracoes_conta') 
            else:
               messages.error(request, 'Ocorreu um erro ao salvar as alterações de perfil. Verifique os campos.')
               # Garante que o formulário de senha esteja limpo
               password_form = CustomPasswordChangeForm(user=request.user)

      elif 'change_password' in request.POST: # <--- PROCESSAMENTO DE SENHA
         # Inicializa o form de senha com os dados POST
         password_form = CustomPasswordChangeForm(user=request.user, data=request.POST) 
         
         if password_form.is_valid():
            user = password_form.save()
            update_session_auth_hash(request, user)  
            messages.success(request, 'Sua senha foi alterada com sucesso!')
            
            # --- CORREÇÃO AQUI ---
            # 1. Obtém a URL base da view
            redirect_url = reverse('configuracoes_conta')
            # 2. Concatena a âncora na URL (String + String)
            redirect_url_with_anchor = redirect_url + '#seguranca'
            # 3. Redireciona para a URL completa
            return redirect(redirect_url_with_anchor)
         else:
            messages.error(request, 'Erro ao alterar a senha. Verifique os campos e sua senha atual.')
            # Garante que os formulários de perfil estejam com a instância atual
            user_form = UserUpdateForm(instance=request.user)
            perfil_form = PerfilUsuarioForm(instance=perfil_instance)

   # --- 2. Inclui todos os formulários no contexto ---
   context = {
      'user_form': user_form,
      'perfil_form': perfil_form,
      'password_form': password_form,
      'consent_form': consent_form,
      'is_admin': is_admin,
   }

   return render(request, 'app_LyfeSync/conta/conta.html', context)

@login_required(login_url='account_login')
def excluir_conta(request):
    """View para processar a exclusão permanente da conta do usuário."""
    if request.method == 'POST':
        # 1. Validação simples de nome de usuário
        confirm_username = request.POST.get('confirm_username')
        
        if confirm_username != request.user.username:
            messages.error(request, 'O nome de usuário não confere. A conta não foi excluída.')
            return redirect(reverse('configuracoes_conta') + '#dados')
        
        # 2. Exclusão de Fato (Transação atômica garante que tudo falhe se algo der errado)
        try:
            with transaction.atomic():
                user_to_delete = request.user
                
                # Desloga o usuário antes de apagar
                # O Django fará um 'cascade delete' que deve apagar PerfilUsuario
                from django.contrib.auth import logout
                logout(request)
                
                # Exclui o objeto User (e PerfilUsuario via cascade se configurado)
                user_to_delete.delete() 

            messages.success(None, 'Sua conta foi excluída permanentemente com sucesso. Sentiremos sua falta.')
            # Redireciona para a página inicial ou de login após a exclusão
            return redirect('home') # Assumindo que 'home' é a URL pública inicial
        
        except Exception as e:
            # Em caso de erro, avisa e redireciona de volta
            messages.error(request, f'Ocorreu um erro interno ao tentar excluir a conta: {e}.')
            return redirect(reverse('configuracoes_conta') + '#dados')

    # Se for um GET, apenas redireciona para a seção de dados
    return redirect(reverse('configuracoes_conta') + '#dados')