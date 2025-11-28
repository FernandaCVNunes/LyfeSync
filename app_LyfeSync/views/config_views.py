# app_LyfeSync/views/config_views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db import transaction
from django.contrib.auth import update_session_auth_hash
from django.urls import reverse
# Importações dos forms e models
from ..forms import UserUpdateForm, PerfilUsuarioForm, CustomPasswordChangeForm, ConsentimentoForm, DicasForm
from ..models import PerfilUsuario, Dicas, HumorTipo
from ._aux_logic import get_humor_map

# -------------------------------------------------------------------
#       Configurações de Dicas
# -------------------------------------------------------------------

# Função de teste para verificar se o usuário é superusuário (Admin)
def is_superuser(user):
    """Retorna True se o usuário for um superusuário ativo."""
    return user.is_active and user.is_superuser

# FUNÇÃO DE TESTE DE AUTORIZAÇÃO (para Dicas)

def is_staff_user(user):
    """Função de teste para o decorador @user_passes_test.
    Verifica se o usuário é staff/administrador (e ativo).
    """
    return user.is_active and user.is_staff

@login_required(login_url='login')
@user_passes_test(is_staff_user, login_url='/') 
def registrar_dica(request):
    """Permite registrar uma nova dica (Admin/Staff ou usuário autorizado)."""
    
    # Lógica de POST e GET
    if request.method == 'POST':
        form = DicasForm(request.POST)
        if form.is_valid():
            dica_obj = form.save(commit=False)
            dica_obj.criado_por = request.user 
            dica_obj.save()
            messages.success(request, "Dica de autocuidado cadastrada com sucesso!")
            return redirect('registrar_dica')
        else:
            messages.error(request, "Erro ao cadastrar dica. Verifique os campos.")
    else:
        form = DicasForm()
    
    try:
        humores_disponiveis = HumorTipo.objects.all().order_by('pk') 
    except NameError:

        humores_disponiveis = []

    humor_map = get_humor_map() 
    
    try:
        dicas_list = Dicas.objects.all().order_by('-data_criacao')
    except Exception:
        dicas_list = []

    context = {
        'form': form,
        'humor_icon_class_map': humor_map, 
        'dicas_list': dicas_list,
        'humores_disponiveis': humores_disponiveis, 
    }
    return render(request, 'app_LyfeSync/autocuidado/dicas.html', context)

@login_required(login_url='login')
@user_passes_test(is_staff_user, login_url='/') 
def alterar_dica(request, dica_id):
    """Permite alterar uma dica existente (Staff/Admin)."""
    
    # 1. Busca a dica ou retorna 404
    dica = get_object_or_404(Dicas, pk=dica_id)
    
    if request.method == 'POST':
        # 2. Popula o formulário com a instância e dados POST
        form = DicasForm(request.POST, instance=dica)
        if form.is_valid():
            form.save()
            messages.success(request, f"Dica '{dica.nomeDica}' alterada com sucesso!")
            # Redireciona de volta para a página principal de gestão de dicas
            return redirect('registrar_dica') 
        else:
            messages.error(request, "Erro ao alterar a dica. Verifique os campos.")

            return registrar_dica(request) 
    
    return redirect('registrar_dica')

@login_required(login_url='login')
@user_passes_test(is_staff_user, login_url='/') 
def excluir_dica(request, dica_id):
    """Permite excluir uma dica existente (Staff/Admin)."""
    
    # 1. Busca a dica ou retorna 404
    dica = get_object_or_404(Dicas, pk=dica_id)
    
    # A exclusão é tipicamente feita com POST (ou DELETE simulado)
    if request.method == 'POST':
        try:
            dica_nome = dica.nomeDica
            dica.delete()
            messages.success(request, f"Dica '{dica_nome}' excluída com sucesso.")
        except Exception as e:
            messages.error(request, f"Erro ao excluir a dica: {e}")
            
        # Redireciona de volta para a lista de dicas
        return redirect('registrar_dica')
    
    # Se for GET, redireciona para evitar acesso direto
    return redirect('registrar_dica')

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