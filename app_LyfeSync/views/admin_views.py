# app_LyfeSync/views/admin_views.py
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from ..forms import DicasForm


# Função de teste para verificar se o usuário é superusuário (Admin)
def is_superuser(user):
    """Retorna True se o usuário for um superusuário ativo."""
    return user.is_active and user.is_superuser

# CORREÇÃO: login_url alterado de 'login' para 'account_login'
@login_required(login_url='account_login') 
@user_passes_test(is_superuser, login_url='home') # Redireciona para home se não for admin
def registrar_dica(request):
    """Permite ao admin registrar uma nova dica."""

    if request.method == 'POST':
        form = DicasForm(request.POST)
        if form.is_valid():
            dica = form.save(commit=False)
            dica.criado_por = request.user
            dica.save()
            messages.success(request, 'Dica cadastrada com sucesso!')
            # Após o sucesso, redireciona para a mesma view para novo registro.
            return redirect('registrar_dica') 
        else:
            messages.error(request, 'Erro ao cadastrar a dica. Verifique os campos.')
    else:
        form = DicasForm()
        
    context = {
        'form': form,
    }
    return render(request, 'app_LyfeSync/humor/dicas.html', context)