# app_LyfeSync/views/report_views.py
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from ..models import Humor
from ._aux_logic import get_humor_map


@login_required
def relatorios(request):
    """Página de menu para relatórios."""
    return render(request, 'app_LyfeSync/relatorios.html')

@login_required
def relatorio_habito(request):
    """Relatório detalhado de hábitos."""
    return render(request, 'app_LyfeSync/relatorioHabito.html')

@login_required
def relatorio_humor(request):
    """
    Gera o relatório de humor, listando todos os registros do usuário 
    em formato de tabela para exibição detalhada, incluindo o ícone do humor.
    """
    humor_map = get_humor_map()
    
    humores_qs = Humor.objects.filter(idusuario=request.user).order_by('-data')
    
    humores_processados = []
    for humor in humores_qs:
        image_path = humor_map.get(humor.estado, 'img/icon/default.png')
        
        try:
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

    return render(request, 'app_LyfeSync/relatorioHumor.html', context)

@login_required
def relatorio_gratidao(request):
    """Relatório detalhado de gratidão."""
    return render(request, 'app_LyfeSync/relatorioGratidao.html')

@login_required
def relatorio_afirmacao(request):
    """Relatório detalhado de afirmação."""
    return render(request, 'app_LyfeSync/relatorioAfirmacao.html')