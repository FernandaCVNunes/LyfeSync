# app_LyfeSync/views/selfcare_views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.utils import timezone
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db.models import F
from datetime import timedelta
import locale
import re
import json
from django.views.decorators.http import require_POST
from ..forms import GratidaoForm, AfirmacaoForm, HumorForm, DicasForm, GratidaoFormSet, AfirmacaoFormSet, AfirmacaoForm
from ..models import Gratidao, Afirmacao, Humor, HumorTipo, Dicas 
from ._aux_logic import get_humor_map

# Configuração de locale para formatação de data/mês em português
# NOTA: Esta configuração é dependente do ambiente (servidor). Se o ambiente não tiver 'pt_BR.utf8' ou 'pt_BR',
# ela falhará silenciosamente ou usará o padrão.
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
    
    # Busca 5 afirmações aleatórias para exibição na página inicial
    afirmacoes = Afirmacao.objects.filter(usuario =request.user).order_by('?')[:5]
    
    context = {'afirmacoes': afirmacoes}
    
    return render(request, 'app_LyfeSync/autocuidado/autocuidado.html', context)


# -------------------------------------------------------------------
# VIEWS DE HUMOR
# -------------------------------------------------------------------
# Variável de regex para ser usada em todas as views, capturando o ID da dica: [DICA ID:X]
DICA_DELIMITADOR = r"\[DICA ID:(\d+)\]"

@login_required(login_url='login')
def humor(request):
    """
    View principal: Exibe o humor de hoje, a dica rotativa (se houver), 
    e o histórico de humor das últimas 2 semanas.
    
    CRÍTICA DE ARQUITETURA: 
    A lógica de persistência da Dica Rotativa (usando DICA_DELIMITADOR) dentro do 
    campo 'descricaohumor' é funcional, mas acopla dados de sistema (ID da Dica) 
    com dados de usuário (descrição). A melhor prática seria adicionar um campo 
    ForeignKey (e.g., 'dica_id') diretamente ao modelo Humor para armazenar a dica,
    removendo a necessidade de regex. O código abaixo mantém a lógica original,
    mas esta é uma área para refatoração futura.
    """
    usuario = request.user
    data_hoje = timezone.localdate()
    
    # 1. Busca o Humor de Hoje
    humor_do_dia = None
    try:
        # Busca o humor e o estado (HumorTipo) relacionado
        humor_do_dia = Humor.objects.select_related('estado').get( 
            usuario=usuario, 
            data=data_hoje
        )
        humor_do_dia.image_path = humor_do_dia.estado.icone
    except Humor.DoesNotExist:
        pass # humor_do_dia continua None

    # --- Variáveis para Dica ---
    dica_do_dia = None
    dica_id_salva = None
    descricao_usuario_original = "" # Inicializa como string vazia
    # ---------------------------

    # 2. Lógica da Dica Rotativa e Persistência (SE JÁ HOUVER REGISTRO DE HUMOR)
    if humor_do_dia:
        humor_tipo_id = humor_do_dia.estado.pk
        
        # A. Tenta extrair o ID da dica e a descrição do usuário do campo descricaohumor
        if humor_do_dia.descricaohumor:
            match = re.match(DICA_DELIMITADOR, humor_do_dia.descricaohumor)
            if match:
                dica_id_salva = int(match.group(1)) # ID da dica (X em [DICA ID:X])
                # Remove o delimitador para obter a descrição original
                descricao_usuario_original = re.sub(DICA_DELIMITADOR, '', humor_do_dia.descricaohumor).strip()
            else:
                # Se não tem a tag, a descrição original é o campo completo
                descricao_usuario_original = humor_do_dia.descricaohumor.strip()

        # Adiciona a descrição limpa para uso no template de hoje
        humor_do_dia.descricao_usuario_original = descricao_usuario_original
        
        # B. Persistência Visual: Tenta encontrar a dica salva para exibição
        if dica_id_salva:
            try:
                dica_do_dia = Dicas.objects.get(pk=dica_id_salva)
            except Dicas.DoesNotExist:
                # Dica não existe mais, prossegue para a lógica de rotação (C)
                pass 
        
        # C. Rotação: Se não há dica salva ou a dica salva foi deletada, faz a rotação
        if not dica_do_dia:
            session_key = f'dicas_vistas_para_humor_{humor_tipo_id}'
            dicas_vistas = request.session.get(session_key, [])
            
            # Tenta pegar uma dica nova (excluindo as já vistas nesta sessão)
            dicas_disponiveis = Dicas.objects.filter(
                humor_relacionado__pk=humor_tipo_id 
            ).exclude(pk__in=dicas_vistas).order_by('?') 
            
            if dicas_disponiveis.exists():
                dica_do_dia = dicas_disponiveis.first()
                dicas_vistas.append(dica_do_dia.pk)
                request.session[session_key] = dicas_vistas
            else:
                # Reinicia a rotação se todas as dicas foram vistas (para o tipo de humor atual)
                if Dicas.objects.filter(humor_relacionado__pk=humor_tipo_id).exists():
                    
                    request.session[session_key] = [] 
                    
                    # Pega a primeira dica após o reset de sessão
                    dica_do_dia = Dicas.objects.filter(humor_relacionado__pk=humor_tipo_id).order_by('?').first() 
                    
                    if dica_do_dia:
                        request.session[session_key] = [dica_do_dia.pk]

        # D. Persistência Final (Salva o ID da nova dica no banco de dados, se ainda não estiver lá)
        if dica_do_dia and not dica_id_salva: 
            # Novo valor do descricaohumor: [DICA ID:X] + descrição original do usuário (se houver)
            novo_desc = f"[DICA ID:{dica_do_dia.pk}] {descricao_usuario_original}"
            
            humor_do_dia.descricaohumor = novo_desc
            humor_do_dia.save(update_fields=['descricaohumor'])
            
    # 3. Lógica do Histórico (Últimas 2 Semanas)
    data_duas_semanas_atras = data_hoje - timedelta(days=14)
    humores_recentes_qs = Humor.objects.select_related('estado').filter(
        usuario=usuario, 
        data__gte=data_duas_semanas_atras
    ).exclude(
        data=data_hoje 
    ).order_by('-data')
    
    humores_recentes_list = []
    
    for registro in humores_recentes_qs:
        registro.image_path = registro.estado.icone 
        
        # CÓDIGO DO HISTÓRICO: Extrai a dica salva e a descrição do usuário
        dica_registro_id = None
        desc_original_reg = registro.descricaohumor
        
        if registro.descricaohumor:
            match = re.match(DICA_DELIMITADOR, registro.descricaohumor)
            if match:
                dica_registro_id = int(match.group(1))
                # Remove o delimitador para obter a descrição original do histórico
                desc_original_reg = re.sub(DICA_DELIMITADOR, '', registro.descricaohumor).strip()
            
            registro.descricaohumor = desc_original_reg # Altera para exibir apenas a descrição do usuário no histórico
        
        # Busca o objeto Dicas (e atribui ao registro)
        if dica_registro_id:
            try:
                registro.dica_utilizada = Dicas.objects.get(pk=dica_registro_id) 
            except Dicas.DoesNotExist:
                registro.dica_utilizada = None

        humores_recentes_list.append(registro)

    # 4. Busca os tipos de humor para o contexto
    tipos_de_humor = HumorTipo.objects.all()
    
    # 5. Contexto: 
    context = {
        'humor_do_dia': humor_do_dia,
        'humores_recentes': humores_recentes_list, 
        'tipos_de_humor': tipos_de_humor,
        'dica_do_dia': dica_do_dia, 
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
            humor_obj.usuario = request.user 
            
            if not humor_obj.data:
                humor_obj.data = timezone.localdate()
            
            try:
                # Nota: A tag [DICA ID:X] é adicionada APENAS na view 'humor' principal, 
                # após o registro, quando a página é carregada.
                humor_obj.save()
                messages.success(request, 'Seu humor foi registrado com sucesso! 😊')
                return redirect('humor')
            except Exception:
                # Erro comum é o UniqueConstraint (usuário+data)
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

@login_required

def alterar_humor(request, humor_id):

    """Permite alterar um Humor existente. Requer login."""

   

    humor_map = get_humor_map()

   

    # 1. Tenta obter a instância do Humor

    instance = get_object_or_404(Humor, idhumor=humor_id, usuario=request.user)

   

    # 2. Lógica de formulário

    if request.method == 'POST':

        # Instancia o formulário com os dados POST e a instância existente (para alteração)

        form = HumorForm(request.POST, instance=instance)

       

        if form.is_valid():

            form.save()

            messages.success(request, 'Humor alterado com sucesso! 🎉')

            return redirect('humor')

        else:

            messages.error(request, 'Erro na validação do formulário. Verifique os campos.')

    else:

        # GET: Inicializa o formulário com os dados da instância

        form = HumorForm(instance=instance)

       

    context = {

        'form': form,

        'humor_icon_class_map': humor_map,

        'humor_id': humor_id,

    }

   

    return render(request, 'app_LyfeSync/humor/alterarHumor.html', context)

@require_POST
@login_required(login_url='login')
def delete_humor(request, humor_id):
    """Exclui um registro de Humor específico e redireciona com mensagem."""
    try:
        # Garante que o usuário só exclua o seu próprio humor.
        humor_instance = get_object_or_404(Humor, pk=humor_id, usuario=request.user)
        humor_data = humor_instance.data.strftime('%d/%m/%Y')
        humor_instance.delete()
        
        # Usa o sistema de mensagens do Django
        messages.success(request, f'Humor da data {humor_data} excluído com sucesso.')
        
    except Exception as e:
        messages.error(request, f'Erro ao excluir o humor: {e}')
        
    # Redireciona sempre para a página principal de humor
    return redirect('humor')


@login_required(login_url='login')
def load_humor_by_date(request):
    """API para buscar dados de humor para uma data específica (via AJAX) e limpando a tag de dica."""
    
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
        
        # CORREÇÃO CRÍTICA: Limpar a descrição removendo a tag [DICA ID:X] antes de enviar ao JS
        cleaned_descricao = re.sub(DICA_DELIMITADOR, '', humor_registro.descricaohumor or "").strip()
        
        data = {
            'exists': True,
            'id': humor_registro.pk, 
            'estado_id': humor_registro.estado.pk,
            'nome_humor': humor_registro.estado.estado, 
            'icone_path': humor_registro.estado.icone, 
            'descricaohumor': cleaned_descricao, # Corrigido: Envia a descrição limpa
        }
        return JsonResponse(data)
        
    except Humor.DoesNotExist:
        return JsonResponse({'exists': False, 'message': 'Nenhum registro encontrado'})
        
    except Exception as e:
        print(f"Erro ao carregar humor no servidor: {e}")
        return JsonResponse({'exists': False, 'error': 'Erro interno do servidor ao buscar humor.'}, status=500)

# -------------------------------------------------------------------
# VIEWS DE DICAS
# -------------------------------------------------------------------

@login_required(login_url='login')
@user_passes_test(is_staff_user, login_url='/') 
def registrar_dica(request):
    """Permite registrar uma nova dica (Admin/Staff ou usuário autorizado)."""
    
    # Lógica de POST e GET
    if request.method == 'POST':
        form = DicasForm(request.POST)
        if form.is_valid():
            dica_obj = form.save(commit=False)
            dica_obj.criado_por = request.user 
            dica_obj.save()
            messages.success(request, "Dica de autocuidado cadastrada com sucesso!")
            return redirect('registrar_dica')
        else:
            messages.error(request, "Erro ao cadastrar dica. Verifique os campos.")
    else:
        form = DicasForm()
    
    # Contexto para exibição da lista de dicas e formulário de registro
    try:
        humores_disponiveis = HumorTipo.objects.all().order_by('pk') 
    except NameError:
        # Caso o modelo HumorTipo não esteja definido no escopo
        humores_disponiveis = []

    humor_map = get_humor_map() 
    
    try:
        dicas_list = Dicas.objects.all().order_by('-data_criacao')
    except Exception:
        dicas_list = []

    context = {
        'form': form,
        'humor_icon_class_map': humor_map, 
        'dicas_list': dicas_list,
        'humores_disponiveis': humores_disponiveis, 
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
            # CORREÇÃO: Em caso de falha na validação, redireciona para a página principal
            # com a mensagem de erro para evitar a chamada recursiva de views.
            messages.error(request, "Erro ao alterar a dica. Verifique os campos.")
            return redirect('registrar_dica')
    
    # Se for GET, redireciona para a página principal (que lista todas as dicas e permite alteração via modal)
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
    ).order_by('-data')[:21] # Limite de 21 gratidões (3 por dia * 7 dias)

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
    
    # Queryset vazio para permitir o registro de novas entradas (não alteração)
    queryset = Gratidao.objects.none() 

    if request.method == 'POST':
        # Instancia o FormSet com os dados do POST
        formset = GratidaoFormSet(request.POST, queryset=queryset)
        
        if formset.is_valid():
            # Lista para armazenar gratidões salvas
            gratidoes_salvas = []
            
            # Itera sobre os formulários no FormSet
            for form in formset:
                # Verifica se o form foi preenchido com conteúdo
                if form.has_changed() and form.cleaned_data.get('conteudo'): 
                    gratidao_obj = form.save(commit=False)
                    gratidao_obj.usuario = request.user 
                    gratidao_obj.data = form.cleaned_data.get('data') # Garante que a data correta seja usada
                    
                    # O save do form já transfere 'conteudo' para 'descricaogratidao' (conforme implementado no form)
                    
                    gratidoes_salvas.append(gratidao_obj)
            
            # Salva todos os objetos de uma vez no banco de dados (otimização)
            if gratidoes_salvas:
                Gratidao.objects.bulk_create(gratidoes_salvas) 
                messages.success(request, f'{len(gratidoes_salvas)} gratidão(ões) registrada(s) com sucesso! 😊')
                return redirect('gratidao') 
            else:
                # Caso o formulário seja válido mas nenhum campo tenha sido preenchido
                messages.error(request, 'Nenhuma gratidão preenchida para salvar.')
                
        else:
            messages.error(request, 'Houve um erro ao registrar sua gratidão. Verifique os campos.')
    else:
        # Se não for POST, inicializa o FormSet vazio, com data atual para 3 formulários
        formset = GratidaoFormSet(queryset=queryset, initial=[{'data': data_hoje}] * 3) 
        
    # Listagem das gratidões da semana para mostrar abaixo do formulário
    gratidoes_da_semana = Gratidao.objects.filter(
        usuario=request.user, 
        data__gte=inicio_semana
    ).order_by('-data')[:21]

    mes_atual_extenso = data_hoje.strftime('%B').capitalize()
        
    context = {
        'formset': formset, 
        'mes_atual': mes_atual_extenso,
        'ano_atual': data_hoje.year,
        'gratidoes_da_semana': gratidoes_da_semana,
    }
    
    return render(request, 'app_LyfeSync/gratidao/registrarGratidao.html', context)

@login_required(login_url='login')
def alterar_gratidao(request, gratidao_id): 
    """Retorna o formulário de alteração (usado para o conteúdo do modal) e processa o POST via AJAX."""
    
    gratidao_instance = get_object_or_404(Gratidao, pk=gratidao_id, usuario=request.user) 
    
    if request.method == 'POST':
        form = GratidaoForm(request.POST, instance=gratidao_instance)
        if form.is_valid():
            form.save()
            # Retorna JSON para o script JS (o script lida com a atualização da UI e fechamento do modal)
            return JsonResponse({'status': 'success', 'message': 'Gratidão alterada com sucesso! 💖'}) 
        else:
            # Em caso de erro, re-renderiza o fragmento HTML do formulário com os erros e retorna o HTML no JSON
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
    """Exclui um registro de Gratidão específico (via POST)."""
    try:
        gratidao_instance = get_object_or_404(Gratidao, pk=gratidao_id, usuario=request.user)
        gratidao_instance.delete()
        messages.success(request, 'Gratidão excluída com sucesso!') 
        return redirect('gratidao') 
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
        'form': AfirmacaoForm() # Passa um formulário vazio (útil se for usado em um modal de registro/alteração)
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
                # Verifica se o campo principal (descricaoafirmacao) foi preenchido
                if form.cleaned_data.get('descricaoafirmacao'): 
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
    Esta view será chamada via AJAX (POST para alteração, GET para dados).
    """
    
    afirmacao_instance = get_object_or_404(Afirmacao, pk=afirmacao_id, usuario=request.user) 
    
    if request.method == 'POST':
        form = AfirmacaoForm(request.POST, instance=afirmacao_instance)
        
        if form.is_valid():
            # O Formset do registro não tem o campo 'data', mas o formulário de alteração (AfirmacaoForm) pode ter.
            form.save()
            # Retorna um JSON para o script do modal
            return JsonResponse({'status': 'success', 'message': 'Afirmação alterada com sucesso! ✨', 'id': afirmacao_id})
        else:
            # Retorna JSON com erros para o modal
            errors = dict(form.errors.items())
            return JsonResponse({'status': 'error', 'message': 'Erro na validação.', 'errors': errors}, status=400)
    else:
        # GET: Retorna os dados para preencher o modal
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