# app_LyfeSync/views/habit_views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import HttpResponse, JsonResponse
from django.contrib.auth.decorators import login_required
from django.utils import timezone
import json 
import locale 
import calendar 
from django.views.decorators.http import require_POST
from ..forms import HabitoForm
from ..models import Habito, StatusDiario, Afirmacao 
from ._aux_logic import _get_checked_days_for_current_month 


@login_required(login_url='login') # Garante que apenas usuários logados acessem
def home_lyfesync(request):
    """Dashboard principal da aplicação para usuários logados."""
    
    # 1. Busca o total de hábitos do usuário
    total_habitos = Habito.objects.filter(usuario=request.user).count()
    
    # 2. Busca a última afirmação registrada (necessário Afirmacao importado)
    # Assumindo que o campo de ligação é 'idusuario'
    ultima_afirmacao = Afirmacao.objects.filter(
        idusuario=request.user
    ).order_by('-data').first()
    
    context = {
        'total_habitos': total_habitos,
        'ultima_afirmacao': ultima_afirmacao
    }
    # CORREÇÃO DE CAMINHO: Template movido para a subpasta 'dashboard'
    return render(request, 'app_LyfeSync/dashboard/homeLyfesync.html', context)


@login_required(login_url='login')
def habito(request):
    """Lista todos os hábitos do usuário e é a página principal de hábitos."""
    
    # 1. Obter lista de hábitos reais
    habitos_reais = Habito.objects.filter(usuario=request.user).order_by('-data_inicio')

    # 2. Configuração de Localidade (para nomes de mês em português)
    try:
        # Tenta a configuração completa
        locale.setlocale(locale.LC_ALL, 'pt_BR.utf8') 
    except locale.Error:
        try:
            # Tenta a configuração simplificada
            locale.setlocale(locale.LC_ALL, 'pt_BR')
        except locale.Error:
            # Falha, usa o padrão do sistema (geralmente inglês)
            pass 
            
    # 3. Transformação de dados (adiciona o mapa de conclusão)
    habitos_para_template = []
    for habito_obj in habitos_reais:
        # Busca o status de conclusão para o mês atual usando a função auxiliar
        checked_days_map = _get_checked_days_for_current_month(habito_obj) 

        habitos_para_template.append({
            'id': habito_obj.id,
            'nome': habito_obj.nome,
            'descricao': habito_obj.descricao, 
            'frequencia': habito_obj.frequencia, 
            # CHAVE ESPERADA PELO TEMPLATE
            'completion_status': checked_days_map 
        })
        
    # 4. Contexto de datas
    month_names = [calendar.month_abbr[i].upper() for i in range(1, 13)]
    dias_do_mes = list(range(1, 32)) 
    
    context = {
        'habitos': habitos_para_template,
        'dias_do_mes': dias_do_mes,
        'mes_atual': timezone.localdate().strftime('%b').upper(),
        'mes_nomes_lista': month_names, 
    }
    
    # CORREÇÃO DE CAMINHO: Template movido para a subpasta 'habitos'
    return render(request, 'app_LyfeSync/habitos/habito.html', context)


# -------------------------------------------------------------------
# VIEWS DE CRIAÇÃO E EDIÇÃO (Formulários)
# -------------------------------------------------------------------

@login_required(login_url='login')
def registrar_habito(request):
    """Permite registrar um novo Habito."""
    if request.method == 'POST':
        form = HabitoForm(request.POST)
        if form.is_valid():
            habito = form.save(commit=False)
            habito.usuario = request.user 
            habito.save()
            messages.success(request, f'Hábito "{habito.nome}" registrado com sucesso!')
            return redirect('habito')
        else:
            messages.error(request, 'Erro ao registrar o hábito. Verifique os campos.')
    else:
        form = HabitoForm()
        
    context = {'form': form}
    # CORREÇÃO DE CAMINHO: Template movido para a subpasta 'habitos'
    return render(request, 'app_LyfeSync/habitos/registrarHabito.html', context)

@login_required(login_url='login')
def alterar_habito(request, habito_id):
    """Permite alterar um Habito existente."""
    # Garante que o hábito existe e pertence ao usuário
    habito_instance = get_object_or_404(Habito, id=habito_id, usuario=request.user) 
    
    if request.method == 'POST':
        form = HabitoForm(request.POST, instance=habito_instance)
        if form.is_valid():
            form.save()
            messages.success(request, f'Hábito "{habito_instance.nome}" alterado com sucesso!')
            return redirect('habito')
        else:
            messages.error(request, 'Erro ao alterar o hábito. Verifique os campos.')
    else:
        form = HabitoForm(instance=habito_instance)
        
    context = {'form': form, 'habito_id': habito_id}
    # CORREÇÃO DE CAMINHO: Template movido para a subpasta 'habitos'
    return render(request, 'app_LyfeSync/habitos/alterarHabito.html', context)


# -------------------------------------------------------------------
# VIEWS DE API PARA HÁBITOS (AJAX/Interação em Tempo Real)
# -------------------------------------------------------------------

@require_POST
@login_required
def toggle_habito_day(request, habit_id, day):
    """
    API: Marca ou desmarca o status de conclusão de um hábito para um dia específico
    (usado na matriz de conclusão na página 'habito').
    """
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        try:
            data = json.loads(request.body)
            action = data.get('action') # 'check' ou 'uncheck'
            
            # 1. Encontra o Hábito e verifica se pertence ao usuário
            habito = get_object_or_404(Habito, pk=habit_id, usuario=request.user)
            
            # 2. Constrói a data (assumindo o mês/ano atual, e apenas o dia é passado)
            date_to_toggle = timezone.localdate().replace(day=int(day))

            # 3. Lógica de toggle/Marcação
            if action == 'check':
                # Cria ou atualiza o StatusDiario para marcar como concluído
                StatusDiario.objects.update_or_create(
                    habito=habito,
                    data_conclusao=date_to_toggle,
                    defaults={'concluido': True}
                )
            elif action == 'uncheck':
                # Remove o StatusDiario (desmarca)
                StatusDiario.objects.filter(
                    habito=habito,
                    data_conclusao=date_to_toggle
                ).delete()
                
            return JsonResponse({'status': 'success', 'habit_id': habit_id, 'day': day, 'action': action})
        except Exception as e:
            # Em caso de erro, retorna status 400 com a mensagem de erro
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
    
    # Se não for uma requisição AJAX POST
    return HttpResponse(status=400)


@require_POST
@login_required
def delete_habit(request, habit_id):
    """API: Exclui um Hábito específico."""
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        try:
            habit = get_object_or_404(Habito, id=habit_id, usuario=request.user)
            habit_nome = habit.nome # Captura o nome antes de deletar
            habit.delete()
            return JsonResponse({'status': 'success', 'message': f'Hábito "{habit_nome}" excluído com sucesso.'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
    return HttpResponse(status=400)