# app_LyfeSync/views/config_views.py
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
# Importações dos forms e models
from ..forms import UserUpdateForm, PerfilUsuarioForm
from ..models import PerfilUsuario 


@login_required(login_url='login')
def conta(request): 
    """Esta view é um atalho que redireciona para a view principal de configuração de conta."""
    return redirect('configuracoes_conta')

@login_required(login_url='login')
def configuracoes_conta(request):
    """Permite ao usuário alterar seus dados e dados de perfil."""
    
    try:
        # Tenta obter o perfil existente (ou levanta DoesNotExist)
        # O Django cria o link user.perfil se o modelo PerfilUsuario estiver configurado com OneToOneField
        perfil_instance = request.user.perfil 
    except PerfilUsuario.DoesNotExist: 
        # Se o perfil não existe, cria uma instância temporária ligada ao usuário
        perfil_instance = PerfilUsuario(user=request.user)
    
    # Inicializa os formulários com as instâncias atuais
    user_form = UserUpdateForm(instance=request.user)
    perfil_form = PerfilUsuarioForm(instance=perfil_instance)
    is_admin = request.user.is_superuser

    if request.method == 'POST':
        # Re-inicializa os formulários com os dados POST
        user_form = UserUpdateForm(request.POST, instance=request.user)
        perfil_form = PerfilUsuarioForm(request.POST, instance=perfil_instance)
        
        with transaction.atomic():
            forms_valid = True

            # Processa o formulário do usuário
            if user_form.is_valid():
                user_form.save()
            else:
                forms_valid = False
                
            # Processa o formulário de perfil
            if perfil_form.is_valid():
                perfil_obj = perfil_form.save(commit=False)
                perfil_obj.user = request.user 
                perfil_obj.save() 
            else:
                forms_valid = False 

            if forms_valid:
                messages.success(request, 'Suas configurações foram atualizadas com sucesso!')
                # Redireciona para evitar reenvio do formulário
                return redirect('configuracoes_conta') 
            else:
                # Se falhar, a mensagem de erro já está definida e o fluxo continua para renderizar
                messages.error(request, 'Ocorreu um erro ao salvar as alterações. Verifique os campos.')

    context = {
        'user_form': user_form,
        'perfil_form': perfil_form,
        'is_admin': is_admin,
    }
    # CORREÇÃO: Template movido para a subpasta 'conta'
    return render(request, 'app_LyfeSync/conta/conta.html', context)