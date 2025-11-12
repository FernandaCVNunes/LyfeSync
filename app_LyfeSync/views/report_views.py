# app_LyfeSync/views/report_views.py
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
# Importação de todos os modelos usados nas views de relatório (mesmo que apenas como stub)
from ..models import Humor, Gratidao, Afirmacao 
from ._aux_logic import get_humor_map


@login_required(login_url='login')
def relatorios(request):
    """Página de menu para relatórios."""
    # CORREÇÃO DE CAMINHO: Template movido para a subpasta 'relatorios'
    return render(request, 'app_LyfeSync/relatorios/relatorios.html')

@login_required(login_url='login')
def relatorio_habito(request):
    """Relatório detalhado de hábitos."""
    # CORREÇÃO DE CAMINHO: Template movido para a subpasta 'relatorios'
    # Futuramente, esta view deve conter a lógica de obtenção e processamento de dados de Habitos/StatusDiario
    return render(request, 'app_LyfeSync/relatorios/relatorioHabito.html')

@login_required(login_url='login')
def relatorio_humor(request):
    """
    Gera o relatório de humor, listando todos os registros do usuário 
    em formato de tabela para exibição detalhada, incluindo o ícone do humor.
    """
    humor_map = get_humor_map()
    
    # Busca todos os registros de humor do usuário, ordenados por data
    humores_qs = Humor.objects.filter(idusuario=request.user).order_by('-data')
    
    humores_processados = []
    for humor in humores_qs:
        # Mapeia o estado de humor para o caminho da imagem do ícone
        image_path = humor_map.get(humor.estado, 'img/icon/default.png')
        
        try:
            # Formata a data para exibição
            data_formatada = humor.data.strftime('%d/%m/%Y')
        except AttributeError:
            data_formatada = 'Data Indefinida'

        humores_processados.append({
            'data': data_formatada,
            'estado': humor.estado,
            'descricaohumor': humor.descricaohumor,
            'image_path': image_path,
        })

    context = {
        'humores_registrados': humores_processados,
    }

    # CORREÇÃO DE CAMINHO: Template movido para a subpasta 'relatorios'
    return render(request, 'app_LyfeSync/relatorios/relatorioHumor.html', context)

@login_required(login_url='login')
def relatorio_gratidao(request):
    """Relatório detalhado de gratidão."""
    # CORREÇÃO DE CAMINHO: Template movido para a subpasta 'relatorios'
    # Futuramente, esta view deve conter a lógica para obter e listar registros de Gratidao
    return render(request, 'app_LyfeSync/relatorios/relatorioGratidao.html')

@login_required(login_url='login')
def relatorio_afirmacao(request):
    """Relatório detalhado de afirmação."""
    # CORREÇÃO DE CAMINHO: Template movido para a subpasta 'relatorios'
    # Futuramente, esta view deve conter a lógica para obter e listar registros de Afirmacao
    return render(request, 'app_LyfeSync/relatorios/relatorioAfirmacao.html')