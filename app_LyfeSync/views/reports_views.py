# app_LyfeSync/views/reports_views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.urls import reverse
from django.views.decorators.http import require_POST
from django.http import JsonResponse, HttpResponse, Http404
from django.contrib import messages
from django.db import transaction, IntegrityError 
from django.utils import timezone
from django.template.loader import render_to_string 
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.forms.models import modelformset_factory
from datetime import timedelta, date, datetime
from io import BytesIO
from xhtml2pdf import pisa
import csv
import calendar
import locale
import re
# Importando os Models reais necessários para as views de relatório
from ..models import Gratidao, Afirmacao, Habito, StatusDiario, Humor, HumorTipo 
from ..forms import HumorForm, DicasForm, RelatorioHumorForm# Importando a lógica auxiliar
from ._aux_logic import _get_report_date_range, get_humor_map, _get_humor_cor_classe, get_humor_icone, get_habitos_e_acompanhamento


# Na exportação em html no style em @page pode definir o formato do A4 por tamnho ou classe do xhtml2pdf
# Retrato: 210mm x 297mm (ou 21cm x 29.7cm) - size: 21cm 29.7cm; -> size: A4 portrait;
# Paisagem: 297mm x 210mm (ou 29.7cm x 21cm)- size: 29.7cm 21cm; -> size: A4 landscape;

# -------------------------------------------------------------------
# LÓGICA AUXILIAR 
# -------------------------------------------------------------------

def get_humor_map(): return {}

def convert_html_to_pdf(source_html, filename, request):
    """Auxiliar para converter o HTML em PDF usando xhtml2pdf."""
    result = BytesIO()
    
    # Define a função de recurso (importante para carregar imagens e CSS externo)
    # Embora seu CSS esteja em <style>, é uma boa prática
    def fetch_resources(uri, rel):
        # A uri será um path absoluto, convertemos para um path do sistema de arquivos
        if uri.startswith(request.build_absolute_uri()):
            # Lida com resources internos se necessário, no seu caso não
            return uri
        return uri 

    pdf = pisa.CreatePDF(
        BytesIO(source_html.encode("utf-8")),  # O conteúdo HTML a ser convertido
        dest=result,                           # O arquivo de destino
        link_callback=fetch_resources          # Função para buscar recursos (opcional, mas recomendado)
    )

    if not pdf.err:
        return HttpResponse(
            result.getvalue(), 
            content_type='application/pdf',
            headers={'Content-Disposition': f'attachment; filename="{filename}"'}
        )
    
    # Se houver erro, retorna uma resposta de erro ou o log
    return HttpResponse('Houve um erro na geração do PDF: %s' % pdf.err, status=500)

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

# -------------------------------------------------------------------
# RELATÓRIO DE HABITO - PDF/CSV
# -------------------------------------------------------------------

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

# -------------------------------------------------------------------
# RELATÓRIO DE GRATIDÃO - PDF/CSV
# -------------------------------------------------------------------

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

    rodape_str = timezone.localtime(timezone.now()).strftime('Gerado por LyfeSync em %d/%m/%Y')

    context = {
        'gratidoes': gratidoes,
        'periodo_str': periodo_str,
        'rodape_content': rodape_str, 
        'total_gratidoes': gratidoes.count(),
        'usuario': request.user.username,
        'data_inicio': data_inicio.strftime('%d/%m/%Y'),
        'data_fim': data_fim.strftime('%d/%m/%Y'),
    }
    # Renderiza o template HTML (otimizado para PDF/impressão)
    html_content = render_to_string('app_LyfeSync/relatorios/pdf_gratidao.html', context)

    # Retorna o HTML com o Content-Type como PDF
    filename = f"relatorio_gratidao_{data_inicio.strftime('%Y%m%d')}_{data_fim.strftime('%Y%m%d')}.pdf"

    return convert_html_to_pdf(html_content, filename, request)

# -------------------------------------------------------------------
# RELATÓRIO DE AFIRMAÇÃO - PDF/CSV
# -------------------------------------------------------------------

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
def exportar_afirmacao_pdf(request):

    """Gera um relatório PDF utilizando xhtml2pdf (Pisa)."""
    hoje = timezone.localdate()
    data_inicio, data_fim, data_referencia, periodo, mes_param, ano_param = _get_report_date_range(request, hoje)

    # 1. Busca dos Registros e Contexto (permanece igual)
    afirmacoes = Afirmacao.objects.filter(
        usuario=request.user,
        data__gte=data_inicio,
        data__lte=data_fim
    ).order_by('-data', '-idafirmacao')
    
    if periodo == 'mensal':
        mes_extenso = data_referencia.strftime('%B').capitalize()
        periodo_str = f"Mensal: {mes_extenso} / {data_referencia.year}"
    elif periodo == 'semanal':
        periodo_str = f"Semanal: {data_inicio.strftime('%d/%m/%Y')} a {data_fim.strftime('%d/%m/%Y')}"
    elif periodo == 'quinzenal':
        periodo_str = f"Quinzenal: {data_inicio.strftime('%d/%m/%Y')} a {data_fim.strftime('%d/%m/%Y')}"
    else:
        periodo_str = "Período Inválido"

    data_rodape = timezone.localtime(timezone.now()).strftime('Gerado por LyfeSync em %d/%m/%Y %H:%M')

    context = {
        'afirmacoes': afirmacoes,
        'periodo_str': periodo_str,
        'now': timezone.now(), 
        'rodape_content': data_rodape,
        'total_afirmacoes': afirmacoes.count(),
        'usuario': request.user.username,
        'data_inicio': data_inicio.strftime('%d/%m/%Y'),
        'data_fim': data_fim.strftime('%d/%m/%Y'),

    }

    # 2. Renderiza o Template HTML
    html_content = render_to_string('app_LyfeSync/relatorios/pdf_afirmacao.html', context)
    
    # 3. Define o nome do arquivo
    filename = f"relatorio_afirmacao_{data_inicio.strftime('%Y%m%d')}_{data_fim.strftime('%Y%m%d')}.pdf"

    # 4. Converte o HTML em PDF e retorna a resposta
    return convert_html_to_pdf(html_content, filename, request)

# -------------------------------------------------------------------
# RELATÓRIO DE HUMOR - PDF/CSV
# -------------------------------------------------------------------

def _get_report_context(usuario, mes, ano):
    """
    Função auxiliar para obter e processar os dados do relatório de humor.
    """
    try:
        data_inicial = date(ano, mes, 1)
        
        # Encontra o último dia do mês
        _, ultimo_dia_do_mes = calendar.monthrange(ano, mes)
        
        data_final = date(ano, mes, ultimo_dia_do_mes)
    except ValueError:
        # Erro de data, retorna 404
        raise Http404("Mês ou ano inválido.")

    # 1. Obter todos os tipos de humor cadastrados
    tipos_humor = list(HumorTipo.objects.all().order_by('estado'))
    
    # 2. Obter os registros de humor para o usuário no período
    registros_do_mes = Humor.objects.filter(
        usuario=usuario,
        data__gte=data_inicial,
        data__lte=data_final
    ).select_related('estado')

    # Mapear o dia do mês para o ID do tipo de humor registrado.
    registros_por_dia = {
        registro.data.day: registro.estado.id_tipo_humor 
        for registro in registros_do_mes
    }

    # 3. Construir a estrutura de dados para o template (a grade)
    report_data = []
    dias_do_mes = range(1, ultimo_dia_do_mes + 1)
    
    # Inicializa a contagem total de dias para cada humor
    contagem_total = {tipo.id_tipo_humor: 0 for tipo in tipos_humor}

    for tipo in tipos_humor:
        estado_nome = tipo.estado
        
        icone_path = get_humor_icone(estado_nome)
        
        cor_fundo = _get_humor_cor_classe(estado_nome) 
        
        # Se você ainda precisar de cor_texto (assumindo que seja branco ou preto para contraste)
        cor_texto = '#000000' # Exemplo: Cor de texto padrão

        registro_diario = {}
        contagem_do_humor = 0
        
        for dia in dias_do_mes:
            # Verifica se o humor deste tipo foi registrado no dia
            humor_registrado = (registros_por_dia.get(dia) == tipo.id_tipo_humor)
            registro_diario[dia] = humor_registrado
            if humor_registrado:
                contagem_do_humor += 1
                
        contagem_total[tipo.id_tipo_humor] = contagem_do_humor

        report_data.append({
            'tipo': tipo,
            'cor_fundo': cor_fundo,    # <-- Usando a cor retornada
            'cor_texto': cor_texto,    # <-- Cor do texto
            'icone_path': icone_path,  # <-- Adicionando o caminho do ícone
            'dias': registro_diario, # {1: True, 2: False, ...}
            'total': contagem_do_humor
        })

    # Calcular o total de dias registrados no mês
    total_dias_registrados = registros_do_mes.count()

    context = {
        'form': RelatorioHumorForm(initial={'mes': mes, 'ano': ano}),
        'mes_extenso': data_inicial.strftime('%B de %Y').capitalize(),
        'dias_do_mes': dias_do_mes,
        'report_data': report_data,
        'ultimo_dia_do_mes': ultimo_dia_do_mes,
        'mes': mes,
        'ano': ano,
        'total_dias_registrados': total_dias_registrados,
        'data_hoje': timezone.now(),
    }
    return context

@login_required
def relatorio_humor(request):
    """
    Exibe o relatório de humor no formato de calendário.
    """
    mes = date.today().month
    ano = date.today().year

    if request.method == 'POST':
        form = RelatorioHumorForm(request.POST)
        if form.is_valid():
            mes = int(form.cleaned_data['mes'])
            ano = int(form.cleaned_data['ano'])
    # Se GET, ou se o formulário for inválido, usa a data atual
    # Para o caso de GET, o form é inicializado no contexto.
    
    try:
        context = _get_report_context(request.user, mes, ano)
    except Http404:
        # Se houver erro de data/contexto, redireciona ou usa o mês atual
        return redirect('relatorio_humor')

    # Garante que o formulário está no contexto, mesmo após o POST inválido
    if 'form' not in context:
        context['form'] = RelatorioHumorForm(initial={'mes': mes, 'ano': ano})
    
    return render(request, 'app_LyfeSync/relatorios/relatorioHumor.html', context)


@login_required
def exportar_humor_csv(request, mes, ano):
    """
    Exporta os dados de humor do mês/ano selecionado para CSV.
    """
    try:
        mes = int(mes)
        ano = int(ano)
    except ValueError:
        return HttpResponse("Parâmetros de data inválidos.", status=400)

    try:
        context = _get_report_context(request.user, mes, ano)
    except Http404:
        return HttpResponse("Dados não encontrados para o período.", status=404)

    # 1. Configurar a resposta HTTP como CSV
    nome_arquivo = f"relatorio_humor_{mes}_{ano}.csv"
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="{nome_arquivo}"'

    writer = csv.writer(response, delimiter=';')
    dias_do_mes = context['dias_do_mes']

    # 2. Escrever o cabeçalho
    header = ['Humor'] + [str(dia) for dia in dias_do_mes] + ['Total no Mês']
    writer.writerow(header)

    # 3. Escrever as linhas de dados
    for data in context['report_data']:
        row = [data['tipo'].estado]
        for dia in dias_do_mes:
            # Escreve 'X' se registrado, vazio se não
            row.append('X' if data['dias'][dia] else '')
        row.append(data['total'])
        writer.writerow(row)

    return response


@login_required
def exportar_humor_pdf(request, mes, ano):
    """
    Exporta o relatório de humor do mês/ano selecionado para PDF.
    
    ATENÇÃO: Este código assume o uso de 'xhtml2pdf'. 
    Você precisará do import: from xhtml2pdf import pisa
    e da instalação: pip install xhtml2pdf
    """
    try:
        # Tenta importar pisa. Se falhar, avisa o usuário.
        from xhtml2pdf import pisa
    except ImportError:
        return HttpResponse("A biblioteca 'xhtml2pdf' não está instalada no ambiente do servidor.", status=500)
    
    try:
        mes = int(mes)
        ano = int(ano)
    except ValueError:
        return HttpResponse("Parâmetros de data inválidos.", status=400)

    try:
        context = _get_report_context(request.user, mes, ano)
    except Http404:
        return HttpResponse("Dados não encontrados para o período.", status=404)

    # Renderiza o template de PDF (relatorioHumor_pdf.html)
    html = render(request, 'app_LyfeSync/relatorios/pdf_humor.html', context).content.decode('utf-8')
    
    # Cria o buffer para o PDF
    buffer = BytesIO()
    pisa_status = pisa.CreatePDF(
        html,                    # O conteúdo HTML
        dest=buffer              # O destino do arquivo (buffer de memória)
    )
    
    if pisa_status.err:
        # Se houve erro na geração do PDF, retorna uma mensagem de erro
        return HttpResponse('Tivemos alguns erros ao gerar o PDF.', status=500)
    
    # Sucesso: Retorna o PDF no response
    nome_arquivo = f"relatorio_humor_{mes}_{ano}.pdf"
    response = HttpResponse(buffer.getvalue(), content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{nome_arquivo}"'
    return response
