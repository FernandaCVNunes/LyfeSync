# app_LyfeSync/views/reports_views.py
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.db import models
import calendar
from datetime import date

# Importando os Models reais necessários para as views de relatório
from ..models import Gratidao, Afirmacao, Habito, StatusDiario 
from ..forms import GratidaoForm, AfirmacaoForm, HumorForm, DicasForm

# Importando a lógica auxiliar
from ._aux_logic import _get_report_date_range, Humor_mock, get_humor_map 


# -------------------------------------------------------------------
# VIEWS DE RELATÓRIOS
# -------------------------------------------------------------------

@login_required(login_url='login')
def relatorios(request):
    """Página principal de Relatórios (LISTAGEM)."""
    # Esta view serve como um índice ou dashboard de relatórios.
    context = {
        'titulo': 'Relatórios e Estatísticas',
        'mensagem': 'Visualize as estatísticas de autocuidado aqui.'
    }
    # Renderize um template simples de listagem de relatórios 
    return render(request, 'app_LyfeSync/relatorios/relatorios.html', context)

@login_required(login_url='login')
def relatorio(request):
    """Placeholder para a view de relatório (singular/detalhado)."""
    # Geralmente redireciona para a listagem ou um relatório padrão.
    return redirect('relatorios')

@login_required(login_url='login')
def relatorio_habito(request):
    """Página de Relatório Específico de Hábito.
    Exibe o progresso mensal dos hábitos ativos.
    """
    # 1. Define o mês e ano de referência
    hoje = timezone.localdate()
    
    try:
        mes_param = int(request.GET.get('mes', hoje.month))
        ano_param = int(request.GET.get('ano', hoje.year))
        data_referencia = hoje.replace(day=1, month=mes_param, year=ano_param)
        
    except (ValueError, TypeError):
        mes_param = hoje.month
        ano_param = hoje.year
        data_referencia = hoje.replace(day=1, month=mes_param, year=ano_param)

    # 2. Determina o último dia do mês e a lista de dias (1 a N)
    ultimo_dia = calendar.monthrange(ano_param, mes_param)[1]
    dias_do_mes = range(1, ultimo_dia + 1)
    
    # 3. Define o intervalo do mês para o filtro
    data_inicio_mes = date(ano_param, mes_param, 1)
    data_fim_mes = date(ano_param, mes_param, ultimo_dia) 

    # 4. Busca os hábitos que estavam ativos DENTRO OU ANTES do mês referenciado
    data_fim_filter = models.Q(data_fim__isnull=True) | models.Q(data_fim__gte=data_inicio_mes)
    
    # Correção do FieldError já aplicada (data_fim_filter como primeiro argumento)
    habitos_ativos = Habito.objects.filter(
        data_fim_filter,                       
        usuario=request.user,                  
        data_inicio__lte=data_fim_mes,         
    ).order_by('nome')
    
    # 5. Busca as marcações (StatusDiario) para todos esses hábitos no mês
    habitos_ids = [h.id for h in habitos_ativos]
    
    status_do_mes = StatusDiario.objects.filter(
        habito_id__in=habitos_ids,
        data__year=ano_param,
        data__month=mes_param,
        concluido=True # <--- CORREÇÃO AQUI: Mudado de 'status=True' para 'concluido=True'
    ).values('habito_id', 'data__day')

    # Mapeia as datas de conclusão: {habito_id: [dia1, dia2, ...]}
    marcacoes_por_habito = {}
    for status in status_do_mes:
        habito_id = status['habito_id']
        dia = status['data__day']
        marcacoes_por_habito.setdefault(habito_id, []).append(dia)

    # 6. Processa e filtra os dados para o template
    dados_relatorio = []
    
    for habito in habitos_ativos:
        dias_concluidos = marcacoes_por_habito.get(habito.id, [])
        total_dias_concluidos = len(dias_concluidos)

        dados_relatorio.append({
            'nome': habito.nome,
            'dias_concluidos': dias_concluidos,
            'total_concluido': total_dias_concluidos,
        })
        
    mes_extenso = calendar.month_name[mes_param].capitalize()

    # 7. Contexto para o template
    context = {
        'titulo': 'Relatório de Hábitos',
        'tipo_relatorio': 'Hábitos Realizados',
        'mes_extenso': mes_extenso,
        'ano_selecionado': ano_param,
        'mes_selecionado': mes_param,
        'dias_do_mes': dias_do_mes, 
        'dados_relatorio': dados_relatorio, 
        'ultimo_dia': ultimo_dia,
        'meses': [(i, calendar.month_name[i].capitalize()) for i in range(1, 13)]
    }
    return render(request, 'app_LyfeSync/relatorios/relatorioHabito.html', context)

@login_required(login_url='login')
def relatorio_gratidao(request):
    """Página de Relatório Específico de Gratidão.
    Exibe a lista de gratidões registradas no período selecionado.
    """
    hoje = timezone.localdate()
    
    # 1. Definição do Intervalo de Tempo usando função auxiliar
    data_inicio, data_fim, data_referencia, periodo, mes_param, ano_param = _get_report_date_range(request, hoje)
    
    # 2. Busca dos Registros de Gratidão
    gratidoes = Gratidao.objects.filter(
        usuario=request.user,
        data__gte=data_inicio,
        data__lte=data_fim
    ).order_by('-data', '-idgratidao') # Mais recente primeiro

    # 3. Formatação do Contexto 
    if periodo == 'mensal':
        mes_extenso = data_referencia.strftime('%B').capitalize()
        periodo_str = f"Mensal: {mes_extenso} / {data_referencia.year}"
    elif periodo == 'semanal':
        periodo_str = f"Semanal: {data_inicio.strftime('%d/%m')} a {data_fim.strftime('%d/%m')} ({data_fim.year})"
    elif periodo == 'quinzenal':
        periodo_str = f"Quinzenal: {data_inicio.strftime('%d/%m')} a {data_fim.strftime('%d/%m')} ({data_fim.year})"
    else:
        periodo_str = "Período Inválido"

    context = {
        'titulo': 'Relatório de Gratidão',
        'tipo_relatorio': 'Gratidões Registradas',
        'gratidoes': gratidoes,
        'meses': [(i, calendar.month_name[i].capitalize()) for i in range(1, 13)],
        'mes_selecionado': mes_param,
        'ano_selecionado': ano_param,
        'periodo_selecionado': periodo,
        'data_inicio': data_inicio.strftime('%Y-%m-%d'), 
        'data_fim': data_fim.strftime('%Y-%m-%d'), 
        'periodo_str': periodo_str, 
        'total_gratidoes': gratidoes.count()
    }
    return render(request, 'app_LyfeSync/relatorios/relatorioGratidao.html', context)


@login_required(login_url='login')
def relatorio_afirmacao(request):
    """Página de Relatório Específico de Afirmação.
    Exibe a lista de afirmações registradas no período selecionado.
    """
    hoje = timezone.localdate()
    
    # 1. Definição do Intervalo de Tempo usando função auxiliar
    data_inicio, data_fim, data_referencia, periodo, mes_param, ano_param = _get_report_date_range(request, hoje)
    
    # 2. Busca dos Registros de Afirmação
    afirmacoes = Afirmacao.objects.filter(
        usuario=request.user,
        data__gte=data_inicio,
        data__lte=data_fim
    ).order_by('-data', '-idafirmacao') # Mais recente primeiro

    # 3. Formatação do Contexto 
    if periodo == 'mensal':
        mes_extenso = data_referencia.strftime('%B').capitalize()
        periodo_str = f"Mensal: {mes_extenso} / {data_referencia.year}"
    elif periodo == 'semanal':
        periodo_str = f"Semanal: {data_inicio.strftime('%d/%m')} a {data_fim.strftime('%d/%m')} ({data_fim.year})"
    elif periodo == 'quinzenal':
        periodo_str = f"Quinzenal: {data_inicio.strftime('%d/%m')} a {data_fim.strftime('%d/%m')} ({data_fim.year})"
    else:
        periodo_str = "Período Inválido"

    context = {
        'titulo': 'Relatório de Afirmações',
        'tipo_relatorio': 'Afirmações Registradas',
        'afirmacoes': afirmacoes,
        'meses': [(i, calendar.month_name[i].capitalize()) for i in range(1, 13)],
        'mes_selecionado': mes_param,
        'ano_selecionado': ano_param,
        'periodo_selecionado': periodo,
        'data_inicio': data_inicio.strftime('%Y-%m-%d'), 
        'data_fim': data_fim.strftime('%Y-%m-%d'), 
        'periodo_str': periodo_str, 
        'total_afirmacoes': afirmacoes.count()
    }
    return render(request, 'app_LyfeSync/relatorios/relatorioAfirmacao.html', context)

@login_required(login_url='login')
def relatorio_humor(request):
    """Página de Relatório Específico de Humor.
    Exibe os registros de humor e estatísticas do período selecionado.
    
    NOTA: Utiliza Humor_mock para simular a consulta ao ORM.
    """
    hoje = timezone.localdate()
    
    # 1. Definição do Intervalo de Tempo usando função auxiliar
    data_inicio, data_fim, data_referencia, periodo, mes_param, ano_param = _get_report_date_range(request, hoje)
    
    # 2. Busca dos Registros de Humor (Usando MOCK)
    registros_humor = Humor_mock.filter(
        usuario=request.user,
        data__gte=data_inicio,
        data__lte=data_fim
    )
    
    if isinstance(registros_humor, list):
        # Ordena pelo campo 'data' (inversamente) e depois por 'idhumor' (inversamente)
        registros_humor = sorted(
            registros_humor, 
            key=lambda r: (r.data, r.idhumor), 
            reverse=True
        )

    # 3. Processamento de Estatísticas
    total_registros = len(registros_humor)
    media_humor = 0
    if total_registros > 0:
        soma_notas = sum(r.notahumor for r in registros_humor)
        media_humor = soma_notas / total_registros

    # Mapeia as notas para nomes de humor (ex: 5 -> 'Excelente')
    humor_map = get_humor_map()
    
    # 4. Formatação do Contexto 
    if periodo == 'mensal':
        mes_extenso = data_referencia.strftime('%B').capitalize()
        periodo_str = f"Mensal: {mes_extenso} / {data_referencia.year}"
    elif periodo == 'semanal':
        periodo_str = f"Semanal: {data_inicio.strftime('%d/%m')} a {data_fim.strftime('%d/%m')} ({data_fim.year})"
    elif periodo == 'quinzenal':
        periodo_str = f"Quinzenal: {data_inicio.strftime('%d/%m')} a {data_fim.strftime('%d/%m')} ({data_fim.year})"
    else:
        periodo_str = "Período Inválido"

    context = {
        'titulo': 'Relatório de Humor',
        'tipo_relatorio': 'Registros de Humor',
        'registros_humor': registros_humor,
        'total_registros': total_registros,
        'media_humor': round(media_humor, 2) if media_humor else 0,
        'humor_map': humor_map,
        'meses': [(i, calendar.month_name[i].capitalize()) for i in range(1, 13)],
        'mes_selecionado': mes_param,
        'ano_selecionado': ano_param,
        'periodo_selecionado': periodo,
        'data_inicio': data_inicio.strftime('%Y-%m-%d'), 
        'data_fim': data_fim.strftime('%Y-%m-%d'), 
        'periodo_str': periodo_str, 
    }
    return render(request, 'app_LyfeSync/relatorios/relatorioHumor.html', context)