# app_LyfeSync/views/habit_views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import HttpResponse, JsonResponse
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from datetime import timedelta
import json
import locale
import calendar
from django.views.decorators.http import require_POST
from ..forms import HabitoForm
from ..models import Habito, StatusDiario, Afirmacao
from ._aux_logic import _get_checked_days_for_current_month # Garanta que este módulo existe

# --- Configuração de Localidade (para nomes de mês/dia em português) ---
try:
    locale.setlocale(locale.LC_ALL, 'pt_BR.utf8')
except locale.Error:
    try:
        locale.setlocale(locale.LC_ALL, 'pt_BR')
    except locale.Error:
        pass # Falha, usa o padrão do sistema (geralmente inglês)
# ----------------------------------------------------------------------

@login_required(login_url='login')
def home_lyfesync(request):
    """
    View principal após o login. Redireciona para o template 'homeLyfesync.html'.
    CORREÇÃO: Template alterado conforme solicitado pelo usuário.
    """
    return render(request, 'app_LyfeSync/dashboard/homeLyfesync.html', {})


@login_required(login_url='login')
def habito(request):
    """Lista todos os hábitos do usuário e é a página principal de hábitos."""
    
    # 1. Obter lista de hábitos reais
    habitos_reais = Habito.objects.filter(usuario=request.user).order_by('-data_inicio')
    
    # -------------------------------------------------------------------
    # 2. LÓGICA DE DATAS (O bloco de 7 dias)
    # -------------------------------------------------------------------
    today = timezone.localdate()
    last_7_days_list = [] # Usaremos uma lista de tuplas para manter a ordem
    
    # Itera para obter os 7 dias, começando 6 dias atrás até hoje
    for i in range(7):
        current_date = today - timedelta(days=6 - i) 
        date_key = current_date.strftime('%Y-%m-%d') 
        # Formato do valor: Nome do dia abreviado (ex: Seg, Ter)
        day_name = current_date.strftime('%a').capitalize().replace('.', '')
        
        # Adiciona a data e o nome do dia na lista
        last_7_days_list.append((date_key, day_name))
        
    # Transforma em dicionário para compatibilidade com o template
    last_7_days_dict = dict(last_7_days_list) 
    # -------------------------------------------------------------------

    # 3. Transformação de dados (adiciona o mapa de conclusão)
    habitos_para_template = []
    for habito_obj in habitos_reais:
        # Busca o status de conclusão para o mês atual usando a função auxiliar
        # NOTA: O aux_logic deve retornar um dicionário como {'YYYY-MM-DD': True/False, ...}
        checked_days_map = _get_checked_days_for_current_month(habito_obj)

        habitos_para_template.append({'id': habito_obj.id,
                      'nome': habito_obj.nome,
                      'descricao': habito_obj.descricao,
                      'frequencia': habito_obj.frequencia,
                      # CHAVE ESPERADA PELO TEMPLATE
                      # O template usa 'date|date:"Y-m-d"' para buscar a chave aqui.
                      'completion_status': checked_days_map}) 
    
    # 4. Contexto final 
    month_names = [calendar.month_abbr[i].upper() for i in range(1, 13)]
    dias_do_mes = list(range(1, 32)) # Variável aparentemente não usada no template atual
    
    context = {
        'habitos': habitos_para_template,
        'last_7_days_dict': last_7_days_dict, # ESSENCIAL para o cabeçalho <th>
        'today_date': today,# ESSENCIAL para marcar o dia 'Hoje'
        
        'dias_do_mes': dias_do_mes,
        'mes_atual': timezone.localdate().strftime('%b').upper(),
        'mes_nomes_lista': month_names,
    }
    
    # CORREÇÃO DE CAMINHO: Template movido para a subpasta 'habitos'
    return render(request, 'app_LyfeSync/habitos/habito.html', context)

# -------------------------------------------------------------------
# Views Requeridas pelo __init__.py e habito.html (Implementações Iniciais)
# -------------------------------------------------------------------

@require_POST
@login_required(login_url='login')
def registrar_habito(request):
    """Processa o formulário de registro de novo hábito."""
    form = HabitoForm(request.POST)
    if form.is_valid():
        habito = form.save(commit=False)
        habito.usuario = request.user
        habito.save()
        messages.success(request, "Hábito registrado com sucesso!")
    else:
        messages.error(request, "Erro ao registrar o hábito. Verifique os campos.")
        
    return redirect('habito')


@require_POST
@login_required(login_url='login')
def alterar_habito(request):
    """Processa o formulário de alteração de hábito."""
    habito_id = request.POST.get('habito_id')
    habito_instance = get_object_or_404(Habito, pk=habito_id, usuario=request.user)
    
    form = HabitoForm(request.POST, instance=habito_instance)
    
    if form.is_valid():
        form.save()
        messages.success(request, "Hábito alterado com sucesso!")
    else:
        messages.error(request, "Erro ao alterar o hábito. Verifique os campos.")
        
    return redirect('habito')


@login_required(login_url='login')
def get_habit_data(request, habit_id):
    """Retorna dados de um hábito específico em formato JSON para preencher o modal de alteração (AJAX)."""
    try:
        habito = Habito.objects.get(pk=habit_id, usuario=request.user)
        return JsonResponse({
            'id': habito.id,
            'nome': habito.nome,
            'descricao': habito.descricao,
            'frequencia': habito.frequencia,
            'data_inicio': habito.data_inicio.strftime('%Y-%m-%d') # Exemplo de formatação de data
        })
    except Habito.DoesNotExist:
        return JsonResponse({'error': 'Hábito não encontrado.'}, status=404)


@require_POST
@login_required(login_url='login')
def toggle_habito_day(request, habit_id, date_string):
    """Alterna o status de conclusão de um hábito para uma data específica (AJAX)."""
    try:
        habito = Habito.objects.get(pk=habit_id, usuario=request.user)
    except Habito.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'Hábito não encontrado.'}, status=404)

    try:
        data = json.loads(request.body)
        is_checked = data.get('is_checked', False)
        date_to_toggle = timezone.datetime.strptime(date_string, '%Y-%m-%d').date()
    except Exception as e:
        return JsonResponse({'success': False, 'message': f'Dados inválidos: {e}'}, status=400)

    # Verifica se a data é futura
    if date_to_toggle > timezone.localdate():
         return JsonResponse({'success': False, 'message': 'Não é possível registrar hábitos para datas futuras.'}, status=400)


    # 1. Busca ou cria o StatusDiario
    # O StatusDiario armazena se o hábito foi concluído naquele dia
    if is_checked:
        # Tenta criar o registro (marcar como concluído)
        status, created = StatusDiario.objects.get_or_create(
            habito=habito,
            data=date_to_toggle,
            defaults={'concluido': True}
        )
        if not created and not status.concluido:
            # Se já existia mas estava desmarcado, atualiza
            status.concluido = True
            status.save()
            
        return JsonResponse({'success': True, 'message': 'Hábito marcado como concluído.'})
    else:
        # A intenção é desmarcar (deletar o registro de StatusDiario se ele existir)
        StatusDiario.objects.filter(habito=habito, data=date_to_toggle).delete() 
        return JsonResponse({'success': True, 'message': 'Hábito desmarcado.'})


@require_POST
@login_required(login_url='login')
def delete_habit(request, habit_id):
    """Exclui um hábito específico (AJAX)."""
    try:
        habito = Habito.objects.get(pk=habit_id, usuario=request.user)
        habito.delete()
        return JsonResponse({'success': True, 'message': 'Hábito excluído com sucesso!'})
    except Habito.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'Hábito não encontrado.'}, status=404)
    except Exception as e:
        return JsonResponse({'success': False, 'message': f'Erro ao excluir: {e}'}, status=500)