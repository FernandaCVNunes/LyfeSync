# app_LyfeSync/views/selfcare_views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.utils import timezone
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required, user_passes_test
from datetime import timedelta
import locale
import json
from django.views.decorators.http import require_POST
from ..forms import GratidaoForm, AfirmacaoForm, HumorForm, DicasForm, GratidaoFormSet, AfirmacaoFormSet, AfirmacaoForm
from ..models import Gratidao, Afirmacao, Humor, HumorTipo, Dicas 
from ._aux_logic import get_humor_map

# Configuração de locale para formatação de data/mês em português
try:
    locale.setlocale(locale.LC_ALL, 'pt_BR.utf8')
except locale.Error:
    try:
        locale.setlocale(locale.LC_ALL, 'pt_BR')
    except:
        pass

# -------------------------------------------------------------------
# FUNÇÃO DE TESTE DE AUTORIZAÇÃO (para Dicas)
# -------------------------------------------------------------------

def is_staff_user(user):
    """Função de teste para o decorador @user_passes_test.
    Verifica se o usuário é staff/administrador (e ativo).
    """
    return user.is_active and user.is_staff

# -------------------------------------------------------------------
# VIEW PRINCIPAL
# -------------------------------------------------------------------

@login_required(login_url='login')
def autocuidado(request):
    """Página de Autocuidado, que pode listar Afirmações, Gratidão e Humor. Requer login."""
    
    afirmacoes = Afirmacao.objects.filter(usuario =request.user).order_by('?')[:5]
    
    context = {'afirmacoes': afirmacoes}
    
    return render(request, 'app_LyfeSync/autocuidado/autocuidado.html', context)


# -------------------------------------------------------------------
# VIEWS DE HUMOR
# -------------------------------------------------------------------

@login_required(login_url='login')
def humor(request):
    """Página de Humor. Requer login."""
    
    data_hoje = timezone.localdate()
    
    # 1. Busca o Humor de Hoje
    try:
        
        humor_do_dia = Humor.objects.select_related('estado').get( 
            usuario =request.user, 
            data=data_hoje
        )
        
        humor_do_dia.image_path = humor_do_dia.estado.icone
    except Humor.DoesNotExist:
        humor_do_dia = None

    # 2. Lógica do Histórico (Últimas 2 Semanas)
    data_duas_semanas_atras = data_hoje - timedelta(days=14)
    
    humores_recentes_qs = Humor.objects.select_related('estado').filter(
        usuario =request.user, 
        data__gte=data_duas_semanas_atras
    ).exclude(
        data=data_hoje 
    ).order_by('-data')
    
    # 3. Adicionar o caminho da imagem aos registros do histórico
    humores_recentes_list = []
    for registro in humores_recentes_qs:
        registro.image_path = registro.estado.icone 
        humores_recentes_list.append(registro)
        
    # 4. Busca os tipos de humor para o contexto (útil para exibir a lista completa de humores no template)
    tipos_de_humor = HumorTipo.objects.all()
    
    context = {
        'humor_do_dia': humor_do_dia,
        'humores_recentes': humores_recentes_list, 
        'tipos_de_humor': tipos_de_humor,
    }
    return render(request, 'app_LyfeSync/humor/humor.html', context)

    
@login_required(login_url='login')
def registrar_humor(request):
    """Permite registrar um novo Humor. Requer login."""
    
    humores_disponiveis = HumorTipo.objects.all()
    
    if request.method == 'POST':
        form = HumorForm(request.POST)
        if form.is_valid():
            humor_obj = form.save(commit=False)
            humor_obj.usuario  = request.user 
            
            if not humor_obj.data:
                humor_obj.data = timezone.localdate()
            
            try:
                humor_obj.save()
                messages.success(request, 'Seu humor foi registrado com sucesso! 😊')
                return redirect('humor')
            except Exception:
                messages.error(request, f'Erro ao salvar: Você já registrou um humor para esta data, ou houve um erro de validação.')
        else:
            messages.error(request, 'Houve um erro ao registrar o humor. Verifique os campos.')
    else:
        form = HumorForm(initial={'data': timezone.localdate()})
        
    context = {
        'form': form,
        'humores_disponiveis': humores_disponiveis 
    }
    return render(request, 'app_LyfeSync/humor/registrarHumor.html', context)

@login_required(login_url='login')
def alterar_humor(request, humor_id): 
    """Permite alterar um Humor existente. Requer login e ID do Humor."""
    
    instance = get_object_or_404(Humor.objects.select_related('estado'), pk=humor_id, usuario =request.user)
    
    # Obtém todos os tipos de humor para o template
    humores_disponiveis = HumorTipo.objects.all()
    
    if request.method == 'POST':
        form = HumorForm(request.POST, instance=instance)
        
        if form.is_valid():
            form.save()
            messages.success(request, 'Humor alterado com sucesso! 🎉')
            return redirect('humor') 
        else:
            messages.error(request, 'Erro na validação do formulário. Verifique os campos.')
    else:
        form = HumorForm(instance=instance)
        
    context = {
        'form': form,
        'humores_disponiveis': humores_disponiveis,
        'humor_id': humor_id, 
        'humor_atual': instance, # Passa a instância para exibir o estado atual
    }
    
    return render(request, 'app_LyfeSync/humor/alterarHumor.html', context)

@require_POST
@login_required(login_url='login')
def delete_humor(request, humor_id):
    """Exclui um registro de Humor específico (via AJAX)."""
    try:
        # Busca o objeto pela Primary Key (pk)
        humor_instance = get_object_or_404(Humor, pk=humor_id, usuario =request.user)
        humor_instance.delete()
        return JsonResponse({'status': 'success', 'message': f'Humor ID {humor_id} excluído.'})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)


@login_required(login_url='login')
def load_humor_by_date(request):
    """API para buscar dados de humor para uma data específica (via AJAX)."""
    
    date_str = request.GET.get('date')
    
    if not date_str:
        return JsonResponse({'exists': False, 'error': 'Data ausente'}, status=400) 
        
    selected_date = None
    
    try:
        # Espera o formato padrão ISO (YYYY-MM-DD)
        selected_date = timezone.datetime.strptime(date_str, '%Y-%m-%d').date()
    except ValueError:
        return JsonResponse({'exists': False, 'error': f'Formato de data inválido. Esperado YYYY-MM-DD.'}, status=400) 
            
    try:
        humor_registro = Humor.objects.select_related('estado').get(usuario =request.user, data=selected_date)
        
        data = {
            'exists': True,
            'id': humor_registro.pk, 
            'nome_humor': humor_registro.estado.estado, 
            'icone_path': humor_registro.estado.icone, 
            'descricaohumor': humor_registro.descricaohumor,
        }
        return JsonResponse(data)
        
    except Humor.DoesNotExist:
        return JsonResponse({'exists': False, 'message': 'Nenhum registro encontrado'})
        
    except Exception as e:
        print(f"Erro ao carregar humor no servidor: {e}")
        return JsonResponse({'exists': False, 'error': 'Erro interno do servidor ao buscar humor.'}, status=500)


@login_required(login_url='login')
@user_passes_test(is_staff_user, login_url='/') 
def registrar_dica(request):
    """Permite registrar uma nova dica (Admin/Staff ou usuário autorizado)."""
    
    if request.method == 'POST':
        form = DicasForm(request.POST)
        if form.is_valid():
            dica_obj = form.save(commit=False)
            dica_obj.criado_por = request.user 
            dica_obj.save() # Salva a dica no banco de dados
            messages.success(request, "Dica de autocuidado cadastrada com sucesso!")
            return redirect('registrar_dica') # Redireciona para a mesma página
        else:
            messages.error(request, "Erro ao cadastrar dica. Verifique os campos.")
    else:
        form = DicasForm()

    # Obtém o mapa de imagens de humor do arquivo auxiliar
    humor_map = get_humor_map() 
    
    # Busca a lista de dicas cadastradas para exibição (assumindo que existe um model 'Dicas')
    try:
        dicas_list = Dicas.objects.all().order_by('-data_criacao')
    except Exception:
        dicas_list = [] # Fallback se houver qualquer erro na busca

    context = {
        'form': form,
        'humor_icon_class_map': humor_map, 
        'dicas_list': dicas_list,
    }
    return render(request, 'app_LyfeSync/dicas/dicas.html', context)
@login_required(login_url='login')
@user_passes_test(is_staff_user, login_url='/') 
def alterar_dica(request, dica_id):
    """Permite alterar uma dica existente (Staff/Admin)."""
    
    # 1. Busca a dica ou retorna 404
    dica = get_object_or_404(Dicas, pk=dica_id)
    
    if request.method == 'POST':
        # 2. Popula o formulário com a instância e dados POST
        form = DicasForm(request.POST, instance=dica)
        if form.is_valid():
            form.save()
            messages.success(request, f"Dica '{dica.nomeDica}' alterada com sucesso!")
            # Redireciona de volta para a página principal de gestão de dicas
            return redirect('registrar_dica') 
        else:
            messages.error(request, "Erro ao alterar a dica. Verifique os campos.")

            return registrar_dica(request) 
    
    return redirect('registrar_dica')

@login_required(login_url='login')
@user_passes_test(is_staff_user, login_url='/') 
def excluir_dica(request, dica_id):
    """Permite excluir uma dica existente (Staff/Admin)."""
    
    # 1. Busca a dica ou retorna 404
    dica = get_object_or_404(Dicas, pk=dica_id)
    
    # A exclusão é tipicamente feita com POST (ou DELETE simulado)
    if request.method == 'POST':
        try:
            dica_nome = dica.nomeDica
            dica.delete()
            messages.success(request, f"Dica '{dica_nome}' excluída com sucesso.")
        except Exception as e:
            messages.error(request, f"Erro ao excluir a dica: {e}")
            
        # Redireciona de volta para a lista de dicas
        return redirect('registrar_dica')
    
    # Se for GET, redireciona para evitar acesso direto
    return redirect('registrar_dica')

# -------------------------------------------------------------------
# VIEWS DE GRATIDÃO
# -------------------------------------------------------------------

@login_required(login_url='login')
def gratidao(request):
    
    data_hoje = timezone.localdate()
    # Calcular o início da semana (segunda-feira)
    # weekday() retorna 0 para segunda e 6 para domingo.
    dias_para_segunda = data_hoje.weekday()
    inicio_semana = data_hoje - timedelta(days=dias_para_segunda)
    
    # Listar registros da semana (limitado a 21, conforme solicitado, embora o limite padrão seja semanal)
    gratidoes_da_semana = Gratidao.objects.filter(
        usuario=request.user, 
        data__gte=inicio_semana
    ).order_by('-data')[:21] # Limite de 21 gratidões

    # Formatação do nome do mês em português (para o título do mês atual)
    mes_atual_extenso = data_hoje.strftime('%B').capitalize()

    context = {
        'gratidoes_da_semana': gratidoes_da_semana, 
        'mes_atual': mes_atual_extenso,
        'ano_atual': data_hoje.year,
        'data_hoje': data_hoje, # Útil para o modal de alteração
    }

    return render(request, 'app_LyfeSync/gratidao/gratidao.html', context)


@login_required(login_url='login') 
def registrar_gratidao(request):
    """Permite registrar até 3 Gratidões de uma vez usando FormSet."""
    
    data_hoje = timezone.localdate()
    # Filtro da semana para exibição
    dias_para_segunda = data_hoje.weekday()
    inicio_semana = data_hoje - timedelta(days=dias_para_segunda)
    
    # Busca gratidões existentes do usuário para o FormSet (se quisermos permitir alteração)
    # Mas, para registrar NOVAS 3 gratidões, inicializamos o queryset vazio.
    queryset = Gratidao.objects.none() 

    if request.method == 'POST':
        # Instancia o FormSet com os dados do POST
        formset = GratidaoFormSet(request.POST, queryset=queryset)
        
        if formset.is_valid():
            # Lista para armazenar gratidões salvas
            gratidoes_salvas = []
            
            # Itera sobre os formulários no FormSet
            for form in formset:
                if form.has_changed() and form.cleaned_data.get('conteudo'): # Verifica se o form foi preenchido
                    gratidao_obj = form.save(commit=False)
                    gratidao_obj.usuario = request.user 
                    gratidao_obj.data = form.cleaned_data.get('data') # Garante que a data correta seja usada
                    
                    # O save do form já transfere 'conteudo' para 'descricaogratidao' (conforme implementado no form)
                    
                    gratidoes_salvas.append(gratidao_obj)
            
            # Salva todos os objetos de uma vez no banco de dados
            if gratidoes_salvas:
                Gratidao.objects.bulk_create(gratidoes_salvas) # Salva múltiplos objetos de forma eficiente
                messages.success(request, f'{len(gratidoes_salvas)} gratidão(ões) registrada(s) com sucesso! 😊')
                return redirect('gratidao') 
            else:
                # Caso o formulário seja válido mas nenhum campo tenha sido preenchido
                messages.error(request, 'Nenhuma gratidão preenchida para salvar.')
                
        else:
            messages.error(request, 'Houve um erro ao registrar sua gratidão. Verifique os campos.')
    else:
        # Se não for POST, inicializa o FormSet vazio
        formset = GratidaoFormSet(queryset=queryset, initial=[{'data': data_hoje}] * 3) 
        
    # Listagem das gratidões da semana para mostrar abaixo do formulário
    gratidoes_da_semana = Gratidao.objects.filter(
        usuario=request.user, 
        data__gte=inicio_semana
    ).order_by('-data')[:21]

    mes_atual_extenso = data_hoje.strftime('%B').capitalize()
        
    context = {
        'formset': formset, # Agora passamos o formset
        'mes_atual': mes_atual_extenso,
        'ano_atual': data_hoje.year,
        'gratidoes_da_semana': gratidoes_da_semana,
    }
    
    return render(request, 'app_LyfeSync/gratidao/registrarGratidao.html', context)

@login_required(login_url='login')
def alterar_gratidao(request, gratidao_id): 
    """Retorna o formulário de alteração (usado para o conteúdo do modal)."""
    
    gratidao_instance = get_object_or_404(Gratidao, pk=gratidao_id, usuario=request.user) 
    
    if request.method == 'POST':
        form = GratidaoForm(request.POST, instance=gratidao_instance)
        if form.is_valid():
            form.save()
            return JsonResponse({'status': 'success', 'message': 'Gratidão alterada com sucesso! 💖'}) 
        else:
            form_html = render(request, 'app_LyfeSync/gratidao/alterarGratidao.html', {'form': form, 'gratidao_id': gratidao_id}).content.decode('utf-8')
            return JsonResponse({'status': 'error', 'message': 'Erro na validação do formulário.', 'form_html': form_html}, status=400)
    else:
        form = GratidaoForm(instance=gratidao_instance)
        
    context = {'form': form, 'gratidao_id': gratidao_id}

    # Esta template deve ser um fragmento HTML (o formulário) para o modal.
    return render(request, 'app_LyfeSync/gratidao/alterarGratidao.html', context)

@require_POST
@login_required(login_url='login')
def delete_gratidao(request, gratidao_id):
    try:
        gratidao_instance = get_object_or_404(Gratidao, pk=gratidao_id, usuario=request.user)
        gratidao_instance.delete()
        messages.success(request, 'Gratidão excluída com sucesso!') 
        return redirect('gratidao') # <<-- REDIRECIONA PARA A PÁGINA PRINCIPAL
    except Exception as e:
        messages.error(request, f'Erro ao excluir a gratidão: {str(e)}')
        return redirect('gratidao')

# -------------------------------------------------------------------
# VIEWS DE AFIRMAÇÃO
# -------------------------------------------------------------------

@login_required(login_url='login')
def afirmacao(request):
    """Exibe o histórico de afirmações com botões de ação e o link para registro."""
    
    # Busca todas as afirmações do usuário, ordenadas da mais recente
    ultimas_afirmacoes = Afirmacao.objects.filter(
        usuario=request.user
    ).order_by('-data', '-idafirmacao') # Adicione idafirmacao para garantir ordem
    
    context = {
        'ultimas_afirmacoes': ultimas_afirmacoes,
        'form': AfirmacaoForm() # Passa um formulário vazio para o modal de alteração
    }

    return render(request, 'app_LyfeSync/afirmacao/afirmacao.html', context)


@login_required(login_url='login')
def registrar_afirmacao(request):
    """Permite registrar 3 novas Afirmações para a mesma data, usando um Formset."""
    
    data_atual = timezone.localdate()
    
    if request.method == 'POST':
        # Instancia o Formset com os dados do POST
        formset = AfirmacaoFormSet(request.POST, 
                                   queryset=Afirmacao.objects.none(), # Formset para novas entradas
                                   prefix='afirmacao')
        
        if formset.is_valid():
            
            # Percorre cada formulário no formset
            for form in formset:
                if form.cleaned_data.get('descricaoafirmacao'): # Garante que o campo não está vazio
                    afirmacao_obj = form.save(commit=False)
                    afirmacao_obj.usuario = request.user
                    afirmacao_obj.data = data_atual # Define a data atual para todos
                    afirmacao_obj.save()
                    
            messages.success(request, '3 Afirmações registradas com sucesso! ✨')
            # Redireciona para a listagem
            return redirect('afirmacao') 
        else:
            # Em caso de erro, re-renderiza a página com o formset preenchido e erros
            messages.error(request, 'Houve um erro ao registrar as afirmações. Verifique os campos.')
    else:
        # GET: Instancia um Formset vazio (com 3 formulários extras)
        formset = AfirmacaoFormSet(queryset=Afirmacao.objects.none(), prefix='afirmacao')
    
    context = {
        'formset': formset,
        'data_atual': data_atual.strftime('%d/%m/%Y'), # Formato para exibição
        'data_input': data_atual.strftime('%Y-%m-%d') # Formato para input type="date"
    }

    return render(request, 'app_LyfeSync/afirmacao/registrarAfirmacao.html', context)


@login_required(login_url='login')
def alterar_afirmacao(request, afirmacao_id):
    """
    Permite alterar uma Afirmação existente. 
    Esta view será chamada via AJAX (POST) pelo modal.
    """
    
    afirmacao_instance = get_object_or_404(Afirmacao, pk=afirmacao_id, usuario=request.user) 
    
    if request.method == 'POST':
        form = AfirmacaoForm(request.POST, instance=afirmacao_instance)
        
        if form.is_valid():
            # O Formset do registro não tem o campo 'data', 
            # mas o formulário de alteração (AfirmacaoForm) precisa para salvar se você adicioná-lo.
            # Se você usar o AfirmacaoForm sem 'data', o valor antigo será mantido.
            form.save()
            # Retorna um JSON para o script do modal
            return JsonResponse({'status': 'success', 'message': 'Afirmação alterada com sucesso! ✨', 'id': afirmacao_id})
        else:
            # Retorna JSON com erros para o modal
            errors = dict(form.errors.items())
            return JsonResponse({'status': 'error', 'message': 'Erro na validação.', 'errors': errors}, status=400)
    else:
        # GET: Esta parte não deve ser renderizada, 
        # mas se for acessada, retorna os dados para preencher o modal
        data = {
            'idafirmacao': afirmacao_instance.idafirmacao,
            'data': afirmacao_instance.data.strftime('%Y-%m-%d') if afirmacao_instance.data else '',
            'descricaoafirmacao': afirmacao_instance.descricaoafirmacao,
            'nomeafirmacao': afirmacao_instance.nomeafirmacao or ''
        }
        return JsonResponse(data)


@require_POST
@login_required(login_url='login')
def delete_afirmacao(request, afirmacao_id):
    """Exclui um registro de Afirmação específico (via POST/AJAX)."""
    try:
        # Busca o objeto pela Primary Key (pk)
        afirmacao_instance = get_object_or_404(Afirmacao, pk=afirmacao_id, usuario=request.user)
        afirmacao_instance.delete()
        # Retorna sucesso para o script JS no afirmacao.html
        return JsonResponse({'status': 'success', 'message': 'Afirmação excluída com sucesso! 🗑️'})
    except Exception as e:
        # Retorna erro em caso de falha
        return JsonResponse({'status': 'error', 'message': f'Erro ao excluir: {str(e)}'}, status=500)