# app_LyfeSync/views/exports_views.py
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from datetime import timedelta, date, datetime
import csv
import calendar
from django.template.loader import render_to_string

# Importando os Models reais necessários para as views de exportação
from ..models import Gratidao, Afirmacao, Humor, HumorTipo
from ..forms import  HumorForm, DicasForm

# Importando a lógica auxiliar e os Mocks necessários
from ._aux_logic import (
    _get_report_date_range, 
    get_habitos_e_acompanhamento,
    _get_humor_cor_classe,
)

# -----------------------------------------------------------
# --- VIEWS DE EXPORTAÇÃO (CSV e PDF/HTML) ---
# -----------------------------------------------------------

@login_required(login_url='login')
def exportar_habito_csv(request):
    """
    Exporta o relatório de acompanhamento de Hábitos do período selecionado
    para um arquivo CSV, detalhando o status diário de cada hábito.
    
    NOTA: Usa a função mock get_habitos_e_acompanhamento para buscar os dados.
    """
    hoje = timezone.localdate()
    # Usa a função auxiliar para definir o intervalo de datas
    data_inicio, data_fim, data_referencia, periodo, mes_param, ano_param = _get_report_date_range(request, hoje)

    # 1. Busca os Hábitos e o Acompanhamento no período (Usando MOCK)
    habitos_processados = get_habitos_e_acompanhamento(request.user, data_inicio, data_fim)
    
    # Lista de todas as datas no período
    delta = data_fim - data_inicio
    dias_periodo = [data_inicio + timedelta(days=i) for i in range(delta.days + 1)]

    # 2. Configura a resposta HTTP para CSV
    filename = f"habitos_{periodo}_{data_inicio.strftime('%Y%m%d')}_{data_fim.strftime('%Y%m%d')}.csv"
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    
    # Adiciona o BOM para garantir que caracteres especiais funcionem no Excel (Português)
    response.write(u'\ufeff'.encode('utf8'))

    # Usa ponto e vírgula como delimitador para melhor compatibilidade com o Excel pt-BR
    writer = csv.writer(response, delimiter=';')

    # 3. Escreve o cabeçalho: 'Hábito' + todas as datas formatadas
    #header_dates = [d.strftime('%d/%m/%Y') for d in dias_periodo]
    writer.writerow(['ID', 'Data', 'Descrição'])

    # 4. Escreve os dados
    for habito in habitos_processados:
        row = [habito['id'], habito['nome']]
        
        for dia in dias_periodo:
            status = habito['acompanhamento'].get(dia)
            
            if status is True:
                row.append('Concluído')
            elif status is False:
                row.append('Não Concluído')
            else:
                row.append('Sem Registro') # Dia sem registro de acompanhamento
        
        writer.writerow(row)

    return response


@login_required(login_url='login')
def exportar_habito_pdf(request):
    """
    Gera um relatório PDF (simulado via HTML formatado para impressão)
    do acompanhamento de Hábitos do período selecionado.
    
    NOTA: Usa a função mock get_habitos_e_acompanhamento para buscar os dados.
    """
    hoje = timezone.localdate()
    data_inicio, data_fim, data_referencia, periodo, mes_param, ano_param = _get_report_date_range(request, hoje)

    # Busca os Hábitos e o Acompanhamento no período (Usando MOCK)
    habitos_processados = get_habitos_e_acompanhamento(request.user, data_inicio, data_fim)

    # Lista de todas as datas no período (necessário para o cabeçalho da tabela)
    delta = data_fim - data_inicio
    dias_periodo = [data_inicio + timedelta(days=i) for i in range(delta.days + 1)]
    
    # Converte a lista de dicionários para uma estrutura mais simples para o template
    habitos_para_template = []
    for h in habitos_processados:
        acompanhamento_map = h['acompanhamento']
        
        # NOVO: Cria uma lista de status ordenados para o template
        status_ordenado = []
        for dia in dias_periodo:
            status = acompanhamento_map.get(dia)
            status_ordenado.append(status)

        habitos_para_template.append({
            'nome': h['nome'],
            'status_diario': status_ordenado, # NOVO CAMPO: Lista ordenada
        })
        
    # Determinação da string do período
    if periodo == 'mensal':
        mes_extenso = data_referencia.strftime('%B').capitalize() 
        periodo_str = f"Mensal: {mes_extenso} / {data_referencia.year}"
    elif periodo == 'semanal':
        periodo_str = f"Semanal: {data_inicio.strftime('%d/%m/%Y')} a {data_fim.strftime('%d/%m/%Y')}"
    elif periodo == 'quinzenal':
        periodo_str = f"Quinzenal: {data_inicio.strftime('%d/%m/%Y')} a {data_fim.strftime('%d/%m/%Y')}"
    else:
        periodo_str = f"Período Personalizado: {data_inicio.strftime('%d/%m/%Y')} a {data_fim.strftime('%d/%m/%Y')}"

    context = {
        'habitos': habitos_para_template,
        'dias_periodo': dias_periodo,
        'periodo_str': periodo_str,
        'data_geracao': timezone.localtime(timezone.now()).strftime('%d/%m/%Y %H:%M'),
        'total_habitos': len(habitos_processados),
        'usuario': request.user.username if request.user.is_authenticated else 'Usuário Não Autenticado',
    }
    
    # Renderiza o template HTML (otimizado para PDF/impressão)
    html_content = render_to_string('app_LyfeSync/relatorios/pdf_habito.html', context)

    # Retorna o HTML com o Content-Type como PDF
    filename = f"relatorio_habitos_{data_inicio.strftime('%Y%m%d')}_{data_fim.strftime('%Y%m%d')}.pdf"

    response = HttpResponse(html_content, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{filename}"'

    return response

@login_required(login_url='login')
def exportar_gratidao_csv(request):
    """Exporta os registros de gratidão do período selecionado para um arquivo CSV."""
    hoje = timezone.localdate()
    # Usa a função auxiliar para definir o intervalo de datas
    data_inicio, data_fim, data_referencia, periodo, mes_param, ano_param = _get_report_date_range(request, hoje)

    # Busca os Registros de Gratidão (Query real)
    gratidoes = Gratidao.objects.filter(
        usuario=request.user,
        data__gte=data_inicio,
        data__lte=data_fim
    ).order_by('-data', '-idgratidao')

    # 1. Configura a resposta HTTP para CSV
    filename = f"gratidao_{periodo}_{data_inicio.strftime('%Y%m%d')}_{data_fim.strftime('%Y%m%d')}.csv"
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    
    # Adiciona o BOM para garantir que caracteres especiais funcionem no Excel
    response.write(u'\ufeff'.encode('utf8'))

    writer = csv.writer(response, delimiter=';') # Use semicolon for better compatibility with pt-BR Excel

    # 2. Escreve o cabeçalho
    writer = csv.writer(response)
    writer.writerow(['ID', 'Data', 'Descrição'])

    for g in gratidoes:
        writer.writerow([
            g.idgratidao,
            g.data.strftime('%Y-%m-%d'), # <-- CAMPO CORRIGIDO: de data_registro para data
            g.descricaogratidao
        ])
        
    return response

@login_required(login_url='login')
def exportar_afirmacao_csv(request):
    """Exporta os registros de afirmação do período selecionado para um arquivo CSV."""
    hoje = timezone.localdate()
    # Usa a função auxiliar para definir o intervalo de datas
    data_inicio, data_fim, data_referencia, periodo, mes_param, ano_param = _get_report_date_range(request, hoje)

    # Busca os Registros de Afirmação (Query real)
    afirmacoes = Afirmacao.objects.filter(
        usuario=request.user,
        data__gte=data_inicio,
        data__lte=data_fim
    ).order_by('-data', '-idafirmacao')

    # 1. Configura a resposta HTTP para CSV
    filename = f"afirmacoes_{periodo}_{data_inicio.strftime('%Y%m%d')}_{data_fim.strftime('%Y%m%d')}.csv"
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    
    # Adiciona o BOM para garantir que caracteres especiais funcionem no Excel
    response.write(u'\ufeff'.encode('utf8'))

    writer = csv.writer(response, delimiter=';') # Use semicolon for better compatibility with pt-BR Excel

    # 2. Escreve o cabeçalho
    writer.writerow(['ID', 'Data', 'Nome da Afirmação', 'Afirmação', 'Data de Registro'])

    # 3. Escreve os dados
    for a in afirmacoes:
        writer.writerow([
            a.idafirmacao,
            a.data.strftime('%d/%m/%Y'),
            a.descricaoafirmacao or '',
            timezone.localtime(a.data_registro).strftime('%d/%m/%Y %H:%M:%S')
        ])

    return response

@login_required(login_url='login')
def exportar_gratidao_pdf(request):
    """Gera um relatório PDF (simulado via HTML formatado para impressão)
    dos registros de gratidão do período selecionado.
    """
    hoje = timezone.localdate()
    data_inicio, data_fim, data_referencia, periodo, mes_param, ano_param = _get_report_date_range(request, hoje)

    # Busca os Registros de Gratidão (Query real)
    gratidoes = Gratidao.objects.filter(
        usuario=request.user,
        data__gte=data_inicio,
        data__lte=data_fim
    ).order_by('-data', '-idgratidao')

    # Determinação da string do período
    if periodo == 'mensal':
        mes_extenso = data_referencia.strftime('%B').capitalize()
        periodo_str = f"Mensal: {mes_extenso} / {data_referencia.year}"
    elif periodo == 'semanal':
        periodo_str = f"Semanal: {data_inicio.strftime('%d/%m/%Y')} a {data_fim.strftime('%d/%m/%Y')}"
    elif periodo == 'quinzenal':
        periodo_str = f"Quinzenal: {data_inicio.strftime('%d/%m/%Y')} a {data_fim.strftime('%d/%m/%Y')}"
    else:
        periodo_str = "Período Inválido"

    context = {
        'gratidoes': gratidoes,
        'periodo_str': periodo_str,
        'data_geracao': timezone.localtime(timezone.now()).strftime('%d/%m/%Y %H:%M'),
        'total_gratidoes': gratidoes.count(),
        'usuario': request.user.username,
        'data_inicio': data_inicio.strftime('%d/%m/%Y'),
        'data_fim': data_fim.strftime('%d/%m/%Y'),
    }

    # Renderiza o template HTML (otimizado para PDF/impressão)
    html_content = render_to_string('app_LyfeSync/relatorios/pdf_gratidao.html', context)

    # Retorna o HTML com o Content-Type como PDF
    filename = f"relatorio_gratidao_{data_inicio.strftime('%Y%m%d')}_{data_fim.strftime('%Y%m%d')}.pdf"
    response = HttpResponse(html_content, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{filename}"'

    return response


@login_required(login_url='login')
def exportar_afirmacao_pdf(request):

    """Gera um relatório PDF (simulado via HTML formatado para impressão)
    dos registros de afirmação do período selecionado.
    """
    hoje = timezone.localdate()
    data_inicio, data_fim, data_referencia, periodo, mes_param, ano_param = _get_report_date_range(request, hoje)

    # Busca os Registros de Afirmação (Query real)
    afirmacoes = Afirmacao.objects.filter(
        usuario=request.user,
        data__gte=data_inicio,
        data__lte=data_fim
    ).order_by('-data', '-idafirmacao')
    
    # Determinação da string do período
    if periodo == 'mensal':
        mes_extenso = data_referencia.strftime('%B').capitalize()
        periodo_str = f"Mensal: {mes_extenso} / {data_referencia.year}"
    elif periodo == 'semanal':
        periodo_str = f"Semanal: {data_inicio.strftime('%d/%m/%Y')} a {data_fim.strftime('%d/%m/%Y')}"
    elif periodo == 'quinzenal':
        periodo_str = f"Quinzenal: {data_inicio.strftime('%d/%m/%Y')} a {data_fim.strftime('%d/%m/%Y')}"
    else:
        periodo_str = "Período Inválido"

    context = {
        'afirmacoes': afirmacoes,
        'periodo_str': periodo_str,
        'data_geracao': timezone.localtime(timezone.now()).strftime('%d/%m/%Y %H:%M'),
        'total_afirmacoes': afirmacoes.count(),
        'usuario': request.user.username,
        'data_inicio': data_inicio.strftime('%d/%m/%Y'),
        'data_fim': data_fim.strftime('%d/%m/%Y'),
    }

    # Renderiza o template HTML (otimizado para PDF/impressão)
    html_content = render_to_string('app_LyfeSync/relatorios/pdf_afirmacao.html', context)

    # Retorna o HTML com o Content-Type como PDF
    filename = f"relatorio_afirmacao_{data_inicio.strftime('%Y%m%d')}_{data_fim.strftime('%Y%m%d')}.pdf"
    response = HttpResponse(html_content, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{filename}"'

    return response


@login_required(login_url='login')
def exportar_humor_csv(request):
    """Exporta os registros de humor (detalhados) para um arquivo CSV."""
    hoje = timezone.localdate()
    data_inicio, data_fim, data_referencia, periodo, mes_param, ano_param = _get_report_date_range(request, hoje)

    # 1. Busca os Registros de Humor (Usando ORM Real)
    registros_humor = Humor.objects.select_related('estado').filter(
        usuario=request.user,
        data__gte=data_inicio,
        data__lte=data_fim
    ).order_by('data_registro')

    # 2. Configura a resposta HTTP para CSV
    filename = f"humor_{data_inicio.strftime('%Y%m%d')}_{data_fim.strftime('%Y%m%d')}.csv"
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    
    response.write(u'\ufeff'.encode('utf8'))
    writer = csv.writer(response, delimiter=';') 

    # 3. Escreve o cabeçalho
    writer.writerow([
        'ID', 'Data', 'Estado do Humor', 'Descrição', 'Data de Registro Completa'
    ])

    # 4. Escreve os dados
    for r in registros_humor:
        writer.writerow([
            r.idhumor,
            r.data.strftime('%d/%m/%Y'),
            r.estado.estado if r.estado else 'N/A', 
            r.descricaohumor or '',
            timezone.localtime(r.data_registro).strftime('%d/%m/%Y %H:%M:%S')
        ])

    return response


@login_required(login_url='login')
def exportar_humor_pdf(request):
    """Gera um relatório PDF (via HTML) do Mood Tracker (tabela)."""
    hoje = timezone.localdate()
    # Força o período mensal para o relatório Mood Tracker
    data_inicio, data_fim, data_referencia, periodo, mes_param, ano_param = _get_report_date_range(request, hoje, default_periodo='mensal')
    
    humor_tipos = HumorTipo.objects.all().order_by('id_tipo_humor')
    
    registros_humor = Humor.objects.select_related('estado').filter(
        usuario=request.user,
        data__gte=data_inicio,
        data__lte=data_fim
    ).order_by('data')

    humor_por_dia = {}
    for r in registros_humor:
        if r.data.day not in humor_por_dia:
            humor_por_dia[r.data.day] = r

    total_dias_marcados = len(humor_por_dia)
    dados_relatorio = []
    
    for humor_tipo in humor_tipos:
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
            'cor_classe': _get_humor_cor_classe(humor_tipo.estado),
            'dias_marcados': dias_marcados,
            'porcentagem': f"{porcentagem:.1f}",
        })

        # 2. Cálculos de Estatísticas (Média do Humor)
        total_registros = len(registros_humor)
        media_humor = None
        if total_registros > 0:
            soma_notas = sum(r.notahumor for r in registros_humor)
            media_humor = soma_notas / total_registros

        # 3. Determinação da string do período
        if periodo == 'mensal':
            mes_extenso = data_referencia.strftime('%B').capitalize() 
            periodo_str = f"Mensal: {mes_extenso} / {data_referencia.year}"
        elif periodo == 'semanal':
            periodo_str = f"Semanal: {data_inicio.strftime('%d/%m/%Y')} a {data_fim.strftime('%d/%m/%Y')}"
        elif periodo == 'quinzenal':
            periodo_str = f"Quinzenal: {data_inicio.strftime('%d/%m/%Y')} a {data_fim.strftime('%d/%m/%Y')}"
        else:
            periodo_str = f"Período Personalizado: {data_inicio.strftime('%d/%m/%Y')} a {data_fim.strftime('%d/%m/%Y')}"

        ultimo_dia = calendar.monthrange(data_referencia.year, data_referencia.month)[1]
        mes_extenso = data_referencia.strftime('%B').capitalize() 
        periodo_str = f"Mensal: {mes_extenso} / {data_referencia.year}"

        context = {
            'periodo_str': periodo_str,
            'data_geracao': timezone.localtime(timezone.now()).strftime('%d/%m/%Y %H:%M'),
            'total_dias_marcados': total_dias_marcados,
            'ultimo_dia': ultimo_dia,
            'dias_do_mes': list(range(1, ultimo_dia + 1)),
            'dados_relatorio': dados_relatorio,
            'usuario': request.user.username,
        }

        # Renderiza o template HTML (otimizado para PDF/impressão)
        html_content = render_to_string('app_LyfeSync/relatorios/pdf_humor.html', context)

        filename = f"relatorio_humor_tracker_{data_referencia.strftime('%Y%m')}.pdf"
        response = HttpResponse(html_content, content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="{filename}"'

        return response