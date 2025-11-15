# app_LyfeSync/views/admin_views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from ..forms import DicasForm
from ..models import Dicas, HumorTipo
from ._aux_logic import get_humor_map


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
    return render(request, 'app_LyfeSync/dicas/dicas.html', context)

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
