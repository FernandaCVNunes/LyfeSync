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
from ..models import Habito, StatusDiario, Afirmacao # Adicionado Afirmacao para home_lyfesync
from ._aux_logic import _get_checked_days_for_current_month # Importa a lógica auxiliar


@login_required
def home_lyfesync(request):
    """Dashboard principal da aplicação para usuários logados."""
    total_habitos = Habito.objects.filter(usuario=request.user).count()
    
    # CORREÇÃO/IMPORTANTE: Usando 'idusuario=request.user' para Afirmacao 
    ultima_afirmacao = Afirmacao.objects.filter(
        idusuario=request.user
    ).order_by('-data').first()
    
    context = {
        'total_habitos': total_habitos,
        'ultima_afirmacao': ultima_afirmacao
    }
    return render(request, 'app_LyfeSync/homeLyfesync.html', context)


@login_required
def habito(request):
    """Lista todos os hábitos do usuário e é a página principal de hábitos."""
    
    # 1. Obter lista de hábitos reais
    try:
        habitos_reais = Habito.objects.filter(usuario=request.user).order_by('-data_inicio')
    except Exception as e:
        print(f"Erro ao buscar hábitos no DB: {e}")
        habitos_reais = [] 

    # 2. Transformação de dados (adiciona o mapa de conclusão)
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
        
    # 3. Contexto de datas
    try:
        locale.setlocale(locale.LC_ALL, 'pt_BR.utf8') 
    except locale.Error:
        try:
            locale.setlocale(locale.LC_ALL, 'pt_BR')
        except locale.Error:
            pass
            
    month_names = [calendar.month_abbr[i].upper() for i in range(1, 13)]
    dias_do_mes = list(range(1, 32)) 
    
    context = {
        'habitos': habitos_para_template,
        'dias_do_mes': dias_do_mes,
        'mes_atual': timezone.localdate().strftime('%b').upper(),
        'mes_nomes_lista': month_names, 
    }
    
    return render(request, 'app_LyfeSync/habito.html', context)


@login_required
def marcar_habito_concluido(request, habito_id):
    """Cria ou atualiza um StatusDiario marcando um hábito como concluído."""
    if request.method == 'POST':
        try:
            habito = get_object_or_404(Habito, pk=habito_id, usuario=request.user) 
            data_hoje = timezone.localdate()

            # Lógica de marcação StatusDiario
            status_diario, criado = StatusDiario.objects.update_or_create(
                habito=habito,
                data_conclusao=data_hoje, # Assumindo 'data_conclusao' é o campo de data
                defaults={'concluido': True}
            )
            
            if criado:
                messages.success(request, f"Parabéns! '{habito.nome}' registrado como concluído hoje.")
            else:
                messages.info(request, f"'{habito.nome}' já estava registrado como concluído hoje.")

            return redirect('habito') 
        except Exception as e:
            messages.error(request, f"Não foi possível concluir a ação: {e}")
            return redirect('habito')

    return HttpResponse(status=405) # Método não permitido se não for POST


# -------------------------------------------------------------------
# VIEWS DE API PARA HÁBITOS (Implementação ORM)
# -------------------------------------------------------------------

@login_required
def registrar_habito(request):
    """Permite registrar um novo Habito. Requer login."""
    if request.method == 'POST':
        form = HabitoForm(request.POST)
        if form.is_valid():
            habito = form.save(commit=False)
            habito.usuario = request.user 
            habito.save()
            return redirect('habito')
    else:
        form = HabitoForm()
        
    context = {'form': form}
    return render(request, 'app_LyfeSync/registrarHabito.html', context)

@login_required
def alterar_habito(request, habito_id):
    """Permite alterar um Habito existente. Requer login e ID do Habito."""
    habito_instance = get_object_or_404(Habito, id=habito_id, usuario=request.user) 
    
    if request.method == 'POST':
        form = HabitoForm(request.POST, instance=habito_instance)
        if form.is_valid():
            form.save()
            return redirect('habito')
    else:
        form = HabitoForm(instance=habito_instance)
        
    context = {'form': form, 'habito_id': habito_id}
    return render(request, 'app_LyfeSync/alterarHabito.html', context)

@require_POST
@login_required
def toggle_habito_day(request, habit_id, day):
    # Lógica da API para marcar/desmarcar StatusDiario
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        try:
            data = json.loads(request.body)
            action = data.get('action') # 'check' ou 'uncheck'
            
            # 1. Encontra o Hábito e verifica se pertence ao usuário
            habito = get_object_or_404(Habito, pk=habit_id, usuario=request.user)
            
            # 2. Constrói a data
            year = timezone.localdate().year
            month = timezone.localdate().month
            date_to_toggle = timezone.localdate().replace(day=int(day)) # Usa localdate e replace

            # 3. Lógica de toggle/Marcação
            if action == 'check':
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
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
    return HttpResponse(status=400)


@require_POST
@login_required
def delete_habit(request, habit_id):
    """Exclui um Hábito específico."""
    try:
        habit = get_object_or_404(Habito, id=habit_id, usuario=request.user)
        habit.delete()
        return JsonResponse({'status': 'success', 'message': f'Hábito ID {habit_id} excluído.'})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)