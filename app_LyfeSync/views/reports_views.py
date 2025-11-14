# app_LyfeSync/views/reports_views.py
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.db import models
import calendar
from datetime import date

# Importando os Models reais necessários para as views de relatório
from ..models import Gratidao, Afirmacao, Habito, StatusDiario, Humor, HumorTipo 
from ..forms import GratidaoForm, AfirmacaoForm, HumorForm, DicasForm

# Importando a lógica auxiliar
from ._aux_logic import _get_report_date_range, _get_humor_cor_classe 


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
    """Página de Relatório Específico de Humor, usando a estrutura Mood Tracker."""
    hoje = timezone.localdate()
    
    # 1. Definição do Intervalo de Tempo (Sempre Mensal para este relatório)
    data_inicio, data_fim, data_referencia, periodo, mes_param, ano_param = _get_report_date_range(request, hoje, default_periodo='mensal')
    
    # 2. Busca dos Tipos de Humor (necessário para as 5 linhas da tabela)
    # Garante 5 tipos: Excelente(5.0) a Péssimo(1.0). Se necessário, adicione um campo de ordenação.
    humor_tipos = HumorTipo.objects.all().order_by('id_tipo_humor') # Use a ordem que desejar
    
    # 3. Busca dos Registros de Humor do período
    # Usamos select_related para buscar o tipo de humor junto, otimizando o acesso ao .estado.icone
    registros_humor = Humor.objects.select_related('estado').filter(
        usuario=request.user,
        data__gte=data_inicio,
        data__lte=data_fim
    ).order_by('data')

    # Mapeamento do dia do mês para o registro de humor (evita duplicidade de dias)
    humor_por_dia = {}
    for r in registros_humor:
        if r.data.day not in humor_por_dia:
            humor_por_dia[r.data.day] = r
            
    # 4. Processamento dos Dados para a Tabela
    total_dias_marcados = len(humor_por_dia)
    dados_relatorio = []
    
    for humor_tipo in humor_tipos: # Itera sobre todos os tipos de humor (5 linhas)
        
        # Lista dos dias em que ESTE tipo de humor foi marcado
        dias_marcados = [
            dia for dia, registro in humor_por_dia.items() 
            if registro.estado.id_tipo_humor == humor_tipo.id_tipo_humor
        ]
        
        num_marcacoes = len(dias_marcados)
        porcentagem = 0.0
        if total_dias_marcados > 0:
            porcentagem = round((num_marcacoes / total_dias_marcados) * 100, 1)

        dados_relatorio.append({
            'tipo': humor_tipo, 
            # ADICIONE A PROPRIEDADE 'cor_classe' AO SEU MODELO HumorTipo (ou mapeie aqui)
            # Como você não forneceu a classe no modelo, vou mapear a partir do 'estado'
            'cor_classe': _get_humor_cor_classe(humor_tipo.estado), 
            'dias_marcados': dias_marcados,
            'porcentagem': f"{porcentagem:.1f}",
        })

    # 5. Formatação do Contexto
    ultimo_dia = calendar.monthrange(data_referencia.year, data_referencia.month)[1]
    mes_extenso = data_referencia.strftime('%B').capitalize()

    context = {
        'hoje': hoje,
        'meses': [(i, calendar.month_name[i].capitalize()) for i in range(1, 13)],
        'mes_extenso': mes_extenso,
        'mes_selecionado': mes_param,
        'ano_selecionado': ano_param,
        'ultimo_dia': ultimo_dia,
        'dias_do_mes': list(range(1, ultimo_dia + 1)),
        'dados_relatorio': dados_relatorio,
        'total_dias_marcados': total_dias_marcados,
    }
    return render(request, 'app_LyfeSync/relatorios/relatorioHumor.html', context)
