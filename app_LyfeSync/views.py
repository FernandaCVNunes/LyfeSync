from django.shortcuts import render

def home(request):
    return render(request, 'app_LyfeSync/home.html')

def sobre_nos(request):
    return render(request, 'app_LyfeSync/sobreNos.html')

def contatos(request):
    return render(request, 'app_LyfeSync/contatos.html')

def login(request):
    return render(request, 'app_LyfeSync/login.html')

def home_lyfesync(request):
    return render(request, 'app_LyfeSync/homeLyfesync.html')

def habito(request):
    return render(request, 'app_LyfeSync/habito.html')

def registrar_habito(request):
    return render(request, 'app_LyfeSync/registrarHabito.html')

def alterar_habito(request):
    return render(request, 'app_LyfeSync/alterarHabito.html')

def autocuidado(request):
    return render(request, 'app_LyfeSync/autocuidado.html')

def humor(request):
    return render(request, 'app_LyfeSync/humor.html')

def gratidao(request):
    return render(request, 'app_LyfeSync/gratidao.html')

def afirmacao(request):
    return render(request, 'app_LyfeSync/afirmacao.html')

def registrar_humor(request):
    return render(request, 'app_LyfeSync/registrarHumor.html')

def alterar_humor(request):
    return render(request, 'app_LyfeSync/alterarHumor.html')

def registrar_gratidao(request):
    return render(request, 'app_LyfeSync/registrarGratidao.html')

def alterar_gratidao(request):
    return render(request, 'app_LyfeSync/alterarGratidao.html')

def registrar_afirmacao(request):
    return render(request, 'app_LyfeSync/registrarAfirmacao.html')

def alterar_afirmacao(request):
    return render(request, 'app_LyfeSync/alterarAfirmacao.html')

def relatorios(request):
    return render(request, 'app_LyfeSync/relatorios.html')

def relatorio_habito(request):
    return render(request, 'app_LyfeSync/relatorioHabito.html')

def relatorio_humor(request):
    return render(request, 'app_LyfeSync/relatorioHumor.html')

def relatorio_gratidao(request):
    return render(request, 'app_LyfeSync/relatorioGratidao.html')

def relatorio_afirmacao(request):
    return render(request, 'app_LyfeSync/relatorioAfirmacao.html')
