# app_LyfeSync/views/_aux_logic.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import HttpResponse, JsonResponse
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from datetime import timedelta, datetime
import json
import locale
import calendar
from django.views.decorators.http import require_POST
from ..forms import HabitoForm
# Assumindo que você tem um modelo chamado StatusDiario para rastrear a conclusão diária
from ..models import Habito, StatusDiario, Afirmacao
from ._aux_logic import _get_checked_days_for_last_7_days

# --- Configuração de Localidade (para nomes de mês/dia em português) ---
# Tenta configurar o locale usando uma lista de fallbacks comuns para pt_BR.
# Isso resolve o FieldError em sistemas onde o locale exato não está instalado.
fallbacks = ['pt_BR.utf8', 'pt_BR', 'pt_BR.UTF-8', 'pt_PT.UTF-8', 'C.UTF-8']
for loc in fallbacks:
    try:
        locale.setlocale(locale.LC_ALL, loc)
        break # Sai do loop se for bem-sucedido
    except locale.Error:
        continue # Tenta o próximo
else:
    # Se o loop terminar sem sucesso (todos falharam),
    # Não define locale, mas evita que a aplicação falhe ao iniciar.
    pass 
# ----------------------------------------------------------------------

@login_required(login_url='login')
def home_lyfesync(request):
    """
    View principal após o login. Redireciona para o template 'homeLyfesync.html'.
    """
    return render(request, 'app_LyfeSync/dashboard/homeLyfesync.html', {})


@login_required(login_url='login')
def habito(request):
    """Lista todos os hábitos do usuário e é a página principal de hábitos."""
    
    # 1. Obter lista de hábitos reais
    habitos_reais = Habito.objects.filter(usuario=request.user).order_by('nome')
    
    # -------------------------------------------------------------------
    # 2. LÓGICA DE DATAS (O bloco de 7 dias)
    # -------------------------------------------------------------------
    today = timezone.localdate()
    last_7_days_list = []
    
    # Itera para obter os 7 dias, começando 6 dias atrás até hoje
    for i in range(7):
        current_date = today - timedelta(days=6 - i)
        date_iso = current_date.strftime('%Y-%m-%d')
        # Formato do dia da semana (ex: Seg) e a data formatada (ex: 13/11)
        day_name = current_date.strftime('%a').capitalize().replace('.', '')
        date_formatted = current_date.strftime('%d/%m') # Adiciona a data formatada
        
        # Adiciona a chave, nome do dia (Seg), e a data formatada (13/11)
        # CORREÇÃO: Usando 'date_iso' para corresponder ao template e adicionando 'is_today'
        last_7_days_list.append({
            'date_iso': date_iso, # Corrigido para corresponder ao uso no template
            'day_name': day_name,
            'date_formatted': date_formatted,
            'is_today': current_date == today # Adicionado para marcar o dia atual no template
        })
        
    # -------------------------------------------------------------------

    # 3. Transformação de dados (adiciona o mapa de conclusão)
    habitos_para_template = []
    for habito_obj in habitos_reais:
        # Usa a nova função para buscar o status dos últimos 7 dias
        checked_days_map = _get_checked_days_for_last_7_days(habito_obj)

        habitos_para_template.append({
            'id': habito_obj.id,
            'nome': habito_obj.nome,
            'descricao': habito_obj.descricao,
            'frequencia': habito_obj.frequencia,
            'completion_status': checked_days_map
        })
    
    
    # 4. Contexto final 
    month_names = [calendar.month_abbr[i].upper() for i in range(1, 13)]
    dias_do_mes = list(range(1, 32))
    
    context = {
        'habitos': habitos_para_template,
        # Passa a lista completa para iterar no template
        'last_7_days_list': last_7_days_list, 
        'today_date': today,
        
        'dias_do_mes': dias_do_mes,
        'mes_atual': timezone.localdate().strftime('%b').upper(),
        'mes_nomes_lista': month_names,
    }
    
    return render(request, 'app_LyfeSync/habitos/habito.html', context)

# -------------------------------------------------------------------
# Views de CRUD e Marcação
# -------------------------------------------------------------------

@require_POST
@login_required(login_url='login')
def registrar_habito(request):
    """Processa o formulário de registro de novo hábito."""
    form = HabitoForm(request.POST)
    if form.is_valid():
        # Adicionar o usuário antes de salvar
        habito = form.save(commit=False)
        habito.usuario = request.user
        habito.save()
        # MENSAGEM DE SUCESSO DE CRIAÇÃO
        messages.success(request, f"Hábito '{habito.nome}' registrado com sucesso!")
    else:
        messages.error(request, "Erro ao registrar o hábito. Verifique os campos.")
        
    return redirect('habito')


@require_POST
@login_required(login_url='login')
def alterar_habito(request, habito_id): 
    """Processa o formulário de alteração de hábito."""
    # Buscar a instância usando o ID da URL e o filtro de usuário
    habito_instance = get_object_or_404(Habito, pk=habito_id, usuario=request.user)
    
    form = HabitoForm(request.POST, instance=habito_instance)
    
    if form.is_valid():
        form.save()
        # MENSAGEM DE SUCESSO DE ALTERAÇÃO
        messages.success(request, f"Hábito '{habito_instance.nome}' alterado com sucesso!")
    else:
        # Se houver erro, podemos carregar o template com o formulário e os erros
        messages.error(request, "Erro ao alterar o hábito. Verifique os campos.")
        
    return redirect('habito')


@login_required(login_url='login')
def get_habit_data(request, habit_id):
    """
    Endpoint de API para retornar dados detalhados de um hábito específico.
    Retorna todos os campos do ModelForm, incluindo 'quantidade' (que era confundido com 'unidade').
    """
    # 2. Funções auxiliares para formatar datas, evitando erro se o campo for nulo
    def format_date_to_iso(date_field):
        if date_field:
            # Se for um objeto datetime, converte para date primeiro
            if isinstance(date_field, datetime):
                date_field = date_field.date()
            return date_field.strftime('%Y-%m-%d')
        return ''

    try:
        # Usando 'usuario=request.user' para consistência
        habito_instance = get_object_or_404(Habito, id=habit_id, usuario=request.user)
        
        # 1. Busca o progresso diário associado (modelos StatusDiario)
        dias_concluidos_obj = StatusDiario.objects.filter(
            habito=habito_instance,
            concluido=True
        ).values_list('data', flat=True)

        # Formata as datas para string para serialização JSON
        dias_concluidos_str = [data.strftime('%Y-%m-%d') for data in dias_concluidos_obj]

        # 3. Formata os dados para retornar como JSON (Incluindo todos os campos necessários)
        data = {
            'id': habito_instance.id,
            'nome': habito_instance.nome,
            'descricao': habito_instance.descricao,
            'frequencia': habito_instance.frequencia, 
            'quantidade': habito_instance.quantidade, 
            'alvo': habito_instance.alvo, 
            # O campo 'unidade' foi removido conforme sua clarificação (era 'quantidade')
            'data_inicio': format_date_to_iso(habito_instance.data_inicio), 
            'data_fim': format_date_to_iso(habito_instance.data_fim), 
            # Assumindo que data_criacao existe no model
            'data_criacao': format_date_to_iso(getattr(habito_instance, 'data_criacao', None)),
            'dias_concluidos': dias_concluidos_str, 
        }

        return JsonResponse(data)
    
    except Habito.DoesNotExist:
        # Se o hábito não existir ou não pertencer ao usuário
        return JsonResponse({'error': 'Hábito não encontrado ou acesso negado.'}, status=404)
    except Exception as e:
        # Tratamento de erro genérico
        # Loga o erro para o desenvolvedor
        print(f"Erro ao buscar dados do hábito {habit_id}: {str(e)}")
        return JsonResponse({'error': f'Erro interno do servidor: Falha ao buscar dados do hábito. Verifique os logs do servidor.'}, status=500)


@require_POST
@login_required(login_url='login')
# O 'day' deve ser a data no formato YYYY-MM-DD
def toggle_habito_day(request, habit_id, day): 
    """
    Alterna o status de conclusão de um hábito para um dia específico.
    """
    # O Django fará a checagem do CSRF token para requisições POST.
    if not request.user.is_authenticated:
        return JsonResponse({'success': False, 'message': 'Não autenticado'}, status=401)
        
    try:
        # Filtra o hábito pelo ID e usuário
        habito = get_object_or_404(Habito, id=habit_id, usuario=request.user) 
        # Tenta converter a string de data (day)
        target_date = datetime.strptime(day, '%Y-%m-%d').date()
    except Habito.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'Hábito não encontrado ou não pertence ao usuário.'}, status=404)
    except ValueError:
        return JsonResponse({'success': False, 'message': 'Formato de data inválido. Use YYYY-MM-DD.'}, status=400)
    except Exception as e:
        # Retorna 400 em caso de erro genérico de processamento
        return JsonResponse({'success': False, 'message': f'Erro de entrada ou processamento: {e}'}, status=400)

    # 1. Tenta buscar/criar o registro StatusDiario
    status_diario, created = StatusDiario.objects.get_or_create(
        habito=habito,
        data=target_date,
        # Se criado, define concluído como True
        defaults={'concluido': True} 
    )

    if created:
        new_status = True
        message = f"Hábito '{habito.nome}' marcado como concluído em {target_date.strftime('%d/%m/%Y')}."
    else:
        # 2b. O registro já existia: inverte o status atual
        status_diario.concluido = not status_diario.concluido
        status_diario.save()
        new_status = status_diario.concluido
        
        if new_status:
            message = f"Marcação de '{habito.nome}' adicionada em {target_date.strftime('%d/%m/%Y')}."
        else:
            message = f"Marcação de '{habito.nome}' removida em {target_date.strftime('%d/%m/%Y')}."
            
    # Retorna o status de sucesso para que o front-end possa exibir a mensagem
    return JsonResponse({
        'success': True, 
        'concluido': new_status,
        'date': day,
        'message': message 
    })

@require_POST
@login_required(login_url='login')
def delete_habit(request, habit_id):
    """Exclui um hábito específico (AJAX). Retorna JSON para o front-end."""
    try:
        # Filtra pelo ID e pelo usuário
        habito = Habito.objects.get(pk=habit_id, usuario=request.user)
        habito_nome = habito.nome
        habito.delete()
        
        # MENSAGEM DE SUCESSO DE EXCLUSÃO (via JSON, para o front-end exibir)
        return JsonResponse({'success': True, 'message': f'Hábito "{habito_nome}" excluído com sucesso!'}) 
    except Habito.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'Hábito não encontrado ou acesso negado.'}, status=404)
    except Exception as e:
        return JsonResponse({'success': False, 'message': f'Erro ao excluir: {e}'}, status=500)