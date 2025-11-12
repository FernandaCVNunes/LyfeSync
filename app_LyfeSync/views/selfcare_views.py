# app_LyfeSync/views/selfcare_views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from datetime import timedelta
import locale
import json
from django.views.decorators.http import require_POST
from ..forms import GratidaoForm, AfirmacaoForm, HumorForm
from ..models import Gratidao, Afirmacao, Humor
from ._aux_logic import get_humor_map # Importa a lógica auxiliar


@login_required(login_url='login')
def autocuidado(request):
    """Página de Autocuidado, que pode listar Afirmações, Gratidão e Humor. Requer login."""
    # CORREÇÃO/IMPORTANTE: Usando 'idusuario' para Afirmacao
    afirmacoes = Afirmacao.objects.filter(idusuario=request.user).order_by('?')[:5]
    
    context = {'afirmacoes': afirmacoes}
    # CORREÇÃO DE CAMINHO: Template movido para a subpasta 'autocuidado'
    return render(request, 'app_LyfeSync/autocuidado/autocuidado.html', context)


# -------------------------------------------------------------------
# VIEWS DE HUMOR
# -------------------------------------------------------------------

@login_required(login_url='login')
def humor(request):
    """Página de Humor. Requer login."""
    
    data_hoje = timezone.localdate()
    humor_map = get_humor_map()
    
    # 1. Busca o Humor de Hoje
    try:
        humor_do_dia = Humor.objects.get(
            idusuario=request.user, 
            data=data_hoje
        )
        humor_do_dia.image_path = humor_map.get(humor_do_dia.estado, 'img/icon/default.png')
    except Humor.DoesNotExist:
        humor_do_dia = None

    # 2. Lógica do Histórico (Últimas 2 Semanas)
    data_duas_semanas_atras = data_hoje - timedelta(days=14)
    
    humores_recentes_qs = Humor.objects.filter(
        idusuario=request.user, 
        data__gte=data_duas_semanas_atras
    ).exclude(
        data=data_hoje 
    ).order_by('-data')
    
    # 3. Adicionar o caminho da imagem aos registros do histórico
    humores_recentes_list = []
    for registro in humores_recentes_qs:
        registro.image_path = humor_map.get(registro.estado, 'img/icon/default.png')
        humores_recentes_list.append(registro)
        
    # 4. Contexto
    context = {
        'humor_do_dia': humor_do_dia,
        'humores_recentes': humores_recentes_list, 
        'humor_icon_class_map': humor_map 
    }
    # CORREÇÃO DE CAMINHO: Template movido para a subpasta 'autocuidado'
    return render(request, 'app_LyfeSync/autocuidado/humor.html', context)

    
@login_required(login_url='login')
def registrar_humor(request):
    """Permite registrar um novo Humor. Requer login."""
    
    humor_icon_class_map = get_humor_map()
    
    if request.method == 'POST':
        form = HumorForm(request.POST)
        if form.is_valid():
            humor_obj = form.save(commit=False)
            humor_obj.idusuario = request.user 
            
            if not humor_obj.data:
                humor_obj.data = timezone.localdate()
            
            try:
                humor_obj.save()
                messages.success(request, 'Seu humor foi registrado com sucesso! 😊')
                return redirect('humor')
            except Exception: # Simplificando a captura de exceção de duplicidade
                messages.error(request, f'Erro ao salvar: Você já registrou um humor para esta data.')
        else:
            messages.error(request, 'Houve um erro ao registrar o humor. Verifique os campos.')
    else:
        form = HumorForm()
        
    context = {
        'form': form,
        'humor_icon_class_map': humor_icon_class_map 
    }
    # CORREÇÃO DE CAMINHO: Template movido para a subpasta 'autocuidado'
    return render(request, 'app_LyfeSync/autocuidado/registrarHumor.html', context)

@login_required(login_url='login')
def alterar_humor(request, humor_id): 
    """Permite alterar um Humor existente. Requer login."""
    
    humor_map = get_humor_map()
    
    # Assume que o campo de ID é idhumor
    instance = get_object_or_404(Humor, idhumor=humor_id, idusuario=request.user)
    
    if request.method == 'POST':
        form = HumorForm(request.POST, instance=instance)
        
        if form.is_valid():
            form.save()
            messages.success(request, 'Humor alterado com sucesso! 🎉')
            return redirect('humor') 
        else:
            messages.error(request, 'Erro na validação do formulário. Verifique os campos.')
    else:
        form = HumorForm(instance=instance)
        
    context = {
        'form': form,
        'humor_icon_class_map': humor_map,
        'humor_id': humor_id, 
    }
    
    # CORREÇÃO DE CAMINHO: Template movido para a subpasta 'autocuidado'
    return render(request, 'app_LyfeSync/autocuidado/alterarHumor.html', context)

@require_POST
@login_required(login_url='login')
def delete_humor(request, humor_id):
    """Exclui um registro de Humor específico (via AJAX)."""
    try:
        humor_instance = get_object_or_404(Humor, idhumor=humor_id, idusuario=request.user)
        humor_instance.delete()
        return JsonResponse({'status': 'success', 'message': f'Humor ID {humor_id} excluído.'})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)


@login_required(login_url='login')
def load_humor_by_date(request):
    """API para buscar dados de humor para uma data específica (via AJAX)."""
    
    date_str = request.GET.get('date')
    
    if not date_str:
        return JsonResponse({'exists': False, 'error': 'Data ausente'}, status=400) 
        
    selected_date = None
    
    try:
        # Tenta o formato padrão ISO (YYYY-MM-DD)
        selected_date = timezone.datetime.strptime(date_str, '%Y-%m-%d').date()
    except ValueError:
        try:
            # Tenta o formato comum brasileiro (DD/MM/YYYY)
            selected_date = timezone.datetime.strptime(date_str, '%d/%m/%Y').date()
        except ValueError:
            return JsonResponse({'exists': False, 'error': f'Formato de data inválido: {date_str}'}, status=400) 
            
    try:
        humor_registro = Humor.objects.get(idusuario=request.user, data=selected_date)
        
        data = {
            'exists': True,
            'id': humor_registro.idhumor, 
            'estado': humor_registro.estado,
            'descricaohumor': humor_registro.descricaohumor,
        }
        return JsonResponse(data)
        
    except Humor.DoesNotExist:
        return JsonResponse({'exists': False, 'message': 'Nenhum registro encontrado'})
        
    except Exception as e:
        print(f"Erro ao carregar humor no servidor: {e}")
        return JsonResponse({'exists': False, 'error': 'Erro interno do servidor ao buscar humor.'}, status=500)


# -------------------------------------------------------------------
# VIEWS DE GRATIDÃO
# -------------------------------------------------------------------

@login_required(login_url='login')
def gratidao(request):
    
    data_hoje = timezone.localdate()
    primeiro_dia_mes = data_hoje.replace(day=1)
    
    gratidoes_do_mes = Gratidao.objects.filter(
        idusuario=request.user, 
        data__gte=primeiro_dia_mes
    ).order_by('-data') 
    
    try:
        # Tenta configurar o locale para exibir o nome do mês corretamente
        locale.setlocale(locale.LC_ALL, 'pt_BR.utf8')
    except locale.Error:
        try:
            locale.setlocale(locale.LC_ALL, 'pt_BR')
        except:
            pass
            
    mes_atual_extenso = data_hoje.strftime('%B').capitalize()

    context = {
        'gratidoes_do_mes': gratidoes_do_mes,
        'mes_atual': mes_atual_extenso,
        'ano_atual': data_hoje.year,
    }

    # CORREÇÃO DE CAMINHO: Template movido para a subpasta 'autocuidado'
    return render(request, 'app_LyfeSync/autocuidado/gratidao.html', context)


@login_required(login_url='login') 
def registrar_gratidao(request):
    """Permite registrar uma nova Gratidão. Requer login."""
    if request.method == 'POST':
        form = GratidaoForm(request.POST)
        if form.is_valid():
            gratidao_obj = form.save(commit=False)
            gratidao_obj.idusuario = request.user 
            
            if not gratidao_obj.data:
                gratidao_obj.data = timezone.localdate()
                
            gratidao_obj.save()
            messages.success(request, 'Sua gratidão foi registrada com sucesso! 😊')
            return redirect('gratidao')
        else:
            messages.error(request, 'Houve um erro ao registrar sua gratidão. Verifique os campos.')
    else:
        form = GratidaoForm()
        
    context = {'form': form}
    # CORREÇÃO DE CAMINHO: Template movido para a subpasta 'autocuidado'
    return render(request, 'app_LyfeSync/autocuidado/registrarGratidao.html', context)


@login_required(login_url='login')
def alterar_gratidao(request, gratidao_id): 
    """Permite alterar uma Gratidao existente. Requer login e ID da Gratidão."""
    
    gratidao_instance = get_object_or_404(Gratidao, idgratidao=gratidao_id, idusuario=request.user) 
    
    if request.method == 'POST':
        form = GratidaoForm(request.POST, instance=gratidao_instance)
        if form.is_valid():
            form.save()
            messages.success(request, 'Gratidão alterada com sucesso! 💖')
            return redirect('gratidao') 
        else:
            messages.error(request, 'Erro na validação do formulário. Verifique os campos.')
    else:
        form = GratidaoForm(instance=gratidao_instance)
        
    context = {'form': form, 'gratidao_id': gratidao_id}
    # CORREÇÃO DE CAMINHO: Template movido para a subpasta 'autocuidado'
    return render(request, 'app_LyfeSync/autocuidado/alterarGratidao.html', context)


@require_POST
@login_required(login_url='login')
def delete_gratidao(request, gratidao_id):
    """Exclui um registro de Gratidão específico (via AJAX)."""
    try:
        gratidao_instance = get_object_or_404(Gratidao, idgratidao=gratidao_id, idusuario=request.user)
        gratidao_instance.delete()
        return JsonResponse({'status': 'success', 'message': f'Gratidão ID {gratidao_id} excluída.'})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)


# -------------------------------------------------------------------
# VIEWS DE AFIRMAÇÃO
# -------------------------------------------------------------------

@login_required(login_url='login')
def afirmacao(request):
    
    ultimas_afirmacoes = Afirmacao.objects.filter(
        idusuario=request.user
    ).order_by('-data')[:15]
    
    context = {
        'ultimas_afirmacoes': ultimas_afirmacoes,
    }

    # CORREÇÃO DE CAMINHO: Template movido para a subpasta 'autocuidado'
    return render(request, 'app_LyfeSync/autocuidado/afirmacao.html', context)


@login_required(login_url='login')
def registrar_afirmacao(request):
    """Permite registrar uma nova Afirmação e redireciona para a listagem."""
    if request.method == 'POST':
        form = AfirmacaoForm(request.POST)
        if form.is_valid():
            afirmacao_obj = form.save(commit=False)
            afirmacao_obj.idusuario = request.user
            
            if not afirmacao_obj.data:
                afirmacao_obj.data = timezone.localdate()
                
            afirmacao_obj.save()
            messages.success(request, 'Afirmação registrada com sucesso! ✨')
            return redirect('afirmacao') 
        else:
            messages.error(request, 'Houve um erro ao registrar a afirmação. Verifique os campos.')
    else:
        form = AfirmacaoForm()
        
    context = {'form': form}
    # CORREÇÃO DE CAMINHO: Template movido para a subpasta 'autocuidado'
    return render(request, 'app_LyfeSync/autocuidado/registrarAfirmacao.html', context)


@login_required(login_url='login')
def alterar_afirmacao(request, afirmacao_id):
    """Permite alterar uma Afirmação existente. Requer login e ID da Afirmação."""
    
    afirmacao_instance = get_object_or_404(Afirmacao, idafirmacao=afirmacao_id, idusuario=request.user) 
    
    if request.method == 'POST':
        form = AfirmacaoForm(request.POST, instance=afirmacao_instance)
        if form.is_valid():
            form.save()
            messages.success(request, 'Afirmação alterada com sucesso! ✨')
            return redirect('afirmacao') # Redireciona para a lista
        else:
            messages.error(request, 'Erro na validação do formulário. Verifique os campos.')
    else:
        form = AfirmacaoForm(instance=afirmacao_instance)
        
    context = {'form': form, 'afirmacao_id': afirmacao_id}
    # CORREÇÃO DE CAMINHO: Template movido para a subpasta 'autocuidado'
    return render(request, 'app_LyfeSync/autocuidado/alterarAfirmacao.html', context)


@require_POST
@login_required(login_url='login')
def delete_afirmacao(request, afirmacao_id):
    """Exclui um registro de Afirmação específico (via AJAX)."""
    try:
        afirmacao_instance = get_object_or_404(Afirmacao, idafirmacao=afirmacao_id, idusuario=request.user)
        afirmacao_instance.delete()
        return JsonResponse({'status': 'success', 'message': f'Afirmação ID {afirmacao_id} excluída.'})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)