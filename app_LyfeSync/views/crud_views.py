# app_LyfeSync/views/crud_views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.contrib.auth.decorators import login_required, user_passes_test
from django.utils import timezone
from datetime import timedelta
import locale
import json
from django.views.decorators.http import require_POST
from django.template.loader import render_to_string 
from ..forms import GratidaoForm, AfirmacaoForm, HumorForm, DicasForm
from ..models import Gratidao, Afirmacao, Humor, HumorTipo, Dicas, Habito, StatusDiario 
# Importando a função utilitária do arquivo auxiliar
from ._aux_logic import get_humor_map 

# Configuração de locale para formatação de data/mês em português
try:
    locale.setlocale(locale.LC_ALL, 'pt_BR.utf8')
except locale.Error:
    try:
        locale.setlocale(locale.LC_ALL, 'pt_BR')
    except:
        pass

# -------------------------------------------------------------------
# FUNÇÃO DE TESTE DE AUTORIZAÇÃO (para Dicas)
# -------------------------------------------------------------------

def is_staff_user(user):
    """Função de teste para o decorador @user_passes_test.
    Verifica se o usuário é staff/administrador (e ativo).
    """
    # Certifique-se de que o usuário é ativo e tem permissão de staff
    return user.is_active and user.is_staff

# -------------------------------------------------------------------
# VIEW PRINCIPAL
# -------------------------------------------------------------------

@login_required(login_url='login')
def autocuidado(request):
    """Página de Autocuidado, que pode listar Afirmações, Gratidão e Humor. Requer login."""
    # Busca 5 afirmações aleatórias do usuário
    afirmacoes = Afirmacao.objects.filter(usuario=request.user).order_by('?')[:5]
    
    context = {'afirmacoes': afirmacoes}
    # Caminho do template
    return render(request, 'app_LyfeSync/autocuidado/autocuidado.html', context)


# -------------------------------------------------------------------
# VIEWS DE HUMOR (CRUD e Listagem)
# -------------------------------------------------------------------

@login_required(login_url='login')
def humor(request):
    """Página de Humor. Requer login."""
    
    data_hoje = timezone.localdate()
    
    # 1. Busca o Humor de Hoje
    try:
        # Usamos select_related('estado') para buscar o objeto HumorTipo
        humor_do_dia = Humor.objects.select_related('estado').get( 
            usuario=request.user, 
            data=data_hoje
        )
        # O caminho do ícone é acessado via 'estado.icone'
        humor_do_dia.image_path = humor_do_dia.estado.icone
    except Humor.DoesNotExist:
        humor_do_dia = None

    # 2. Lógica do Histórico (Últimas 2 Semanas)
    data_duas_semanas_atras = data_hoje - timedelta(days=14)
    
    # Usamos select_related('estado') para otimizar a busca do objeto HumorTipo
    humores_recentes_qs = Humor.objects.select_related('estado').filter(
        usuario=request.user, 
        data__gte=data_duas_semanas_atras
    ).exclude(
        data=data_hoje 
    ).order_by('-data')
    
    # 3. Adicionar o caminho da imagem aos registros do histórico
    humores_recentes_list = []
    for registro in humores_recentes_qs:
        # Acessa diretamente o icone do objeto relacionado via 'estado.icone'
        registro.image_path = registro.estado.icone 
        humores_recentes_list.append(registro)
        
    # 4. Busca os tipos de humor para o contexto (útil para exibir a lista completa de humores no template)
    tipos_de_humor = HumorTipo.objects.all()
    
    context = {
        'humor_do_dia': humor_do_dia,
        'humores_recentes': humores_recentes_list, 
        'tipos_de_humor': tipos_de_humor,
    }
    # Caminho do template
    return render(request, 'app_LyfeSync/humor/humor.html', context)

    
@login_required(login_url='login')
def registrar_humor(request):
    """Permite registrar um novo Humor. Requer login."""
    
    # Obtém todos os tipos de humor disponíveis para o formulário/template (usando o icone)
    humores_disponiveis = HumorTipo.objects.all()
    
    if request.method == 'POST':
        form = HumorForm(request.POST)
        if form.is_valid():
            humor_obj = form.save(commit=False)
            
            humor_obj.usuario = request.user 
            
            if not humor_obj.data:
                humor_obj.data = timezone.localdate()
            
            try:
                humor_obj.save()
                messages.success(request, 'Seu humor foi registrado com sucesso! 😊')
                return redirect('humor')
            except Exception: # Captura exceção de duplicidade (unique_together) ou outras falhas
                messages.error(request, 'Erro ao salvar: Você já registrou um humor para esta data, ou houve um erro de validação.')
        else:
            messages.error(request, 'Houve um erro ao registrar o humor. Verifique os campos.')
    else:
        # Inicializa o formulário com a data de hoje
        form = HumorForm(initial={'data': timezone.localdate()})
        
    context = {
        'form': form,
        'humores_disponiveis': humores_disponiveis 
    }
    # Caminho do template
    return render(request, 'app_LyfeSync/humor/registrarHumor.html', context)

@login_required(login_url='login')
def alterar_humor(request, humor_id): 
    """Permite alterar um Humor existente. Requer login e ID do Humor."""
    
    # Busca o registro de Humor usando select_related('estado')
    instance = get_object_or_404(Humor.objects.select_related('estado'), pk=humor_id, usuario=request.user)
    
    # Obtém todos os tipos de humor para o template
    humores_disponiveis = HumorTipo.objects.all()
    
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
        'humores_disponiveis': humores_disponiveis,
        'humor_id': humor_id, 
        'humor_atual': instance, # Passa a instância para exibir o estado atual
    }
    
    # Caminho do template
    return render(request, 'app_LyfeSync/humor/alterarHumor.html', context)

@require_POST
@login_required(login_url='login')
def delete_humor(request, humor_id):
    """Exclui um registro de Humor específico (via AJAX)."""
    try:
        # Busca o objeto pela Primary Key (pk)
        humor_instance = get_object_or_404(Humor, pk=humor_id, usuario=request.user)
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
        # Espera o formato padrão ISO (YYYY-MM-DD)
        selected_date = timezone.datetime.strptime(date_str, '%Y-%m-%d').date()
    except ValueError:
        return JsonResponse({'exists': False, 'error': f'Formato de data inválido. Esperado YYYY-MM-DD.'}, status=400) 
            
    try:
        # Usando select_related('estado') para buscar o tipo de humor junto
        humor_registro = Humor.objects.select_related('estado').get(usuario=request.user, data=selected_date)
        
        data = {
            'exists': True,
            'id': humor_registro.pk, 
            # Acessar nome e ícone via 'estado.estado' e 'estado.icone'
            'nome_humor': humor_registro.estado.estado, 
            'icone_path': humor_registro.estado.icone, 
            'descricaohumor': humor_registro.descricaohumor,
        }
        return JsonResponse(data)
        
    except Humor.DoesNotExist:
        return JsonResponse({'exists': False, 'message': 'Nenhum registro encontrado'})
        
    except Exception as e:
        print(f"Erro ao carregar humor no servidor: {e}")
        return JsonResponse({'exists': False, 'error': 'Erro interno do servidor ao buscar humor.'}, status=500)

# -------------------------------------------------------------------
# VIEWS DE DICAS (APENAS REGISTRO)
# -------------------------------------------------------------------

@login_required(login_url='login')
@user_passes_test(is_staff_user, login_url='/') # Restringe o acesso a usuários Staff/Admin.
def registrar_dica(request):
    """Permite registrar uma nova dica (Admin/Staff ou usuário autorizado)."""
    
    if request.method == 'POST':
        form = DicasForm(request.POST)
        if form.is_valid():
            dica_obj = form.save(commit=False)
            dica_obj.criado_por = request.user # Assumindo que o campo é 'criado_por' no modelo Dicas
            dica_obj.save() # Salva a dica no banco de dados
            messages.success(request, "Dica de autocuidado cadastrada com sucesso!")
            return redirect('registrar_dica') # Redireciona para a mesma página
        else:
            messages.error(request, "Erro ao cadastrar dica. Verifique os campos.")
    else:
        form = DicasForm()

    # Obtém o mapa de imagens de humor do arquivo auxiliar
    humor_map = get_humor_map() 
    
    # Busca a lista de dicas cadastradas para exibição
    try:
        dicas_list = Dicas.objects.all().order_by('-data_criacao')
    except Exception:
        dicas_list = [] # Fallback se houver qualquer erro na busca

    context = {
        'form': form,
        'humor_icon_class_map': humor_map, 
        'dicas_list': dicas_list,
    }
    return render(request, 'app_LyfeSync/humor/dicas.html', context)

# -------------------------------------------------------------------
# VIEWS DE GRATIDÃO (CRUD e Listagem)
# -------------------------------------------------------------------

@login_required(login_url='login')
def gratidao(request):
    """Página de Gratidão. Lista todas as gratidões do mês atual."""
    
    data_hoje = timezone.localdate()
    primeiro_dia_mes = data_hoje.replace(day=1)
    
    
    gratidoes_do_mes = Gratidao.objects.filter(
        usuario=request.user, 
        data__gte=primeiro_dia_mes
    ).order_by('-data') 
    
    # Formatação do nome do mês em português
    mes_atual_extenso = data_hoje.strftime('%B').capitalize()

    context = {
        'gratidoes_do_mes': gratidoes_do_mes,
        'mes_atual': mes_atual_extenso,
        'ano_atual': data_hoje.year,
    }

    # Caminho do template
    return render(request, 'app_LyfeSync/gratidao/gratidao.html', context)


@login_required(login_url='login') 
def registrar_gratidao(request):
    """Permite registrar uma nova Gratidão. Requer login."""
    if request.method == 'POST':
        form = GratidaoForm(request.POST)
        if form.is_valid():
            gratidao_obj = form.save(commit=False)
            
            gratidao_obj.usuario = request.user 
            
            if not gratidao_obj.data:
                gratidao_obj.data = timezone.localdate()
                
            gratidao_obj.save()
            messages.success(request, 'Sua gratidão foi registrada com sucesso! 😊')
            return redirect('gratidao')
        else:
            messages.error(request, 'Houve um erro ao registrar sua gratidão. Verifique os campos.')
    else:
        form = GratidaoForm(initial={'data': timezone.localdate()})
        
    context = {'form': form}
    # Caminho do template
    return render(request, 'app_LyfeSync/gratidao/registrarGratidao.html', context)


@login_required(login_url='login')
def alterar_gratidao(request, gratidao_id): 
    """Permite alterar uma Gratidao existente. Requer login e ID da Gratidão."""
    
    # Busca o objeto pela Primary Key (pk)
    gratidao_instance = get_object_or_404(Gratidao, pk=gratidao_id, usuario=request.user) 
    
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
    # Caminho do template
    return render(request, 'app_LyfeSync/gratidao/alterarGratidao.html', context)


@require_POST
@login_required(login_url='login')
def delete_gratidao(request, gratidao_id):
    """Exclui um registro de Gratidão específico (via AJAX)."""
    try:
        # Busca o objeto pela Primary Key (pk)
        gratidao_instance = get_object_or_404(Gratidao, pk=gratidao_id, usuario=request.user)
        gratidao_instance.delete()
        return JsonResponse({'status': 'success', 'message': f'Gratidão ID {gratidao_id} excluída.'})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)


# -------------------------------------------------------------------
# VIEWS DE AFIRMAÇÃO (CRUD e Listagem)
# -------------------------------------------------------------------

@login_required(login_url='login')
def afirmacao(request):
    """Página de Afirmações. Lista as últimas afirmações do usuário."""
    
    
    ultimas_afirmacoes = Afirmacao.objects.filter(
        usuario=request.user
    ).order_by('-data')[:15]
    
    context = {
        'ultimas_afirmacoes': ultimas_afirmacoes,
    }

    # Caminho do template
    return render(request, 'app_LyfeSync/afirmacao/afirmacao.html', context)


@login_required(login_url='login')
def registrar_afirmacao(request):
    """Permite registrar uma nova Afirmação e redireciona para a listagem."""
    if request.method == 'POST':
        form = AfirmacaoForm(request.POST)
        if form.is_valid():
            afirmacao_obj = form.save(commit=False)
            
            afirmacao_obj.usuario = request.user
            
            if not afirmacao_obj.data:
                afirmacao_obj.data = timezone.localdate()
                
            afirmacao_obj.save()
            messages.success(request, 'Afirmação registrada com sucesso! ✨')
            return redirect('afirmacao') 
        else:
            messages.error(request, 'Houve um erro ao registrar a afirmação. Verifique os campos.')
    else:
        form = AfirmacaoForm(initial={'data': timezone.localdate()})
        
    context = {'form': form}
    # Caminho do template
    return render(request, 'app_LyfeSync/afirmacao/registrarAfirmacao.html', context)


@login_required(login_url='login')
def alterar_afirmacao(request, afirmacao_id):
    """Permite alterar uma Afirmação existente. Requer login e ID da Afirmação."""
    
    # Busca o objeto pela Primary Key (pk)
    afirmacao_instance = get_object_or_404(Afirmacao, pk=afirmacao_id, usuario=request.user) 
    
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
    # Caminho do template
    return render(request, 'app_LyfeSync/afirmacao/alterarAfirmacao.html', context)


@require_POST
@login_required(login_url='login')
def delete_afirmacao(request, afirmacao_id):
    """Exclui um registro de Afirmação específico (via AJAX)."""
    try:
        # Busca o objeto pela Primary Key (pk)
        afirmacao_instance = get_object_or_404(Afirmacao, pk=afirmacao_id, usuario=request.user)
        afirmacao_instance.delete()
        return JsonResponse({'status': 'success', 'message': f'Afirmação ID {afirmacao_id} excluída.'})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)