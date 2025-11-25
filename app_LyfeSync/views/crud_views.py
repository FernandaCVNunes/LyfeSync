# app_LyfeSync/views/crud_views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.urls import reverse
from django.views.decorators.http import require_POST
from django.http import JsonResponse, HttpResponse
from django.contrib import messages
from django.db import transaction, IntegrityError 
from django.utils import timezone
from django.template.loader import render_to_string 
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.forms.models import modelformset_factory
from datetime import timedelta, date, datetime
import locale
import re

try:
    # Tenta importar mocks se estiver em um ambiente de exportação/teste
    from ._aux_logic import (Humor, HumorTipo, Dicas, Habito, StatusDiario, MockUser, HumorForm, DicasForm, 
    get_humor_map, extract_dica_info, rebuild_descricaohumor)
except ImportError:
    from ..forms import (GratidaoCreateForm, GratidaoUpdateForm, AfirmacaoBaseForm, AfirmacaoRegistroForm, AfirmacaoAlteracaoForm,
    HumorForm, DicasForm)
    from ..models import Gratidao, Afirmacao, Humor, HumorTipo, Dicas, Habito, StatusDiario
    
    # Funções auxiliares (stubs, se não estiverem em _aux_logic)
    def get_humor_map(): return {}
    def extract_dica_info(desc): 
        """Extrai o ID da dica [DICA ID:X] da descrição."""
        match = re.search(r"\[DICA ID:(\d+)\]", desc)
        dica_id = int(match.group(1)) if match else None
        descricao_limpa = re.sub(r"\[DICA ID:(\d+)\]", "", desc).strip()
        return dica_id, descricao_limpa

    def rebuild_descricaohumor(dica_id, desc): 
        """Reconstrói a descrição com a tag da dica."""
        if dica_id:
            return f"[DICA ID:{dica_id}] {desc}"
        return desc

    
    # MockUser de fallback para contexto (apesar de não ser usado nas views decoradas)
    class MockUser:
        def __init__(self, username="mock_user"): self.username = username
        @property
        def is_authenticated(self): return True


# Configuração de locale para formatação de data/mês em português
try:
    # Tenta um formato comum
    locale.setlocale(locale.LC_ALL, 'pt_BR.utf8')
except locale.Error:
    try:
        # Tenta um formato alternativo
        locale.setlocale(locale.LC_ALL, 'pt_BR')
    except:
        pass # Falha silenciosamente se o locale não estiver disponível

# -------------------------------------------------------------------
# FUNÇÃO DE TESTE DE AUTORIZAÇÃO E VARIÁVEIS GLOBAIS
# -------------------------------------------------------------------

def is_staff_user(user):
    """Função de teste para o decorador @user_passes_test.
    Verifica se o usuário é staff/administrador (e ativo).
    """
    return user.is_active and user.is_staff

# Variável de regex global para ser usada em todas as views, capturando o ID da dica: [DICA ID:X]
DICA_DELIMITADOR = r"\[DICA ID:(\d+)\]"

# -------------------------------------------------------------------
# VIEW PRINCIPAL DE AUTOCUIDADO
# -------------------------------------------------------------------

@login_required(login_url='login')
def autocuidado(request):
    """Página de Autocuidado, que pode listar Afirmações, Gratidão e Humor. Requer login."""
    # Busca 5 afirmações aleatórias do usuário
    afirmacoes = Afirmacao.objects.filter(usuario=request.user).order_by('?')[:5]
    
    context = {'afirmacoes': afirmacoes}
    return render(request, 'app_LyfeSync/autocuidado/autocuidado.html', context)


# -------------------------------------------------------------------
# VIEWS DE HUMOR (CRUD e Listagem)
# -------------------------------------------------------------------

@login_required(login_url='login')
def humor(request):
    """
    View principal: Exibe o humor de hoje, a dica rotativa (se houver), 
    e o histórico de humor das últimas 2 semanas.
    """
    usuario = request.user
    data_hoje = timezone.localdate()
    
    # 1. Busca o Humor de Hoje
    humor_do_dia = None
    try:
        # Usa select_related para buscar o estado do humor em uma única query (otimização)
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
    descricao_usuario_original = "" 
    # ---------------------------

    # 2. Lógica da Dica Rotativa e Persistência (SE JÁ HOVER REGISTRO DE HUMOR)
    if humor_do_dia:
        humor_tipo_id = humor_do_dia.estado.pk
        
        # A. Extrai o ID da dica e a descrição do usuário (USANDO FUNÇÃO AUXILIAR)
        # Assumindo que extract_dica_info retorna (dica_id, descricao_limpa)
        dica_id_salva, descricao_usuario_original = extract_dica_info(humor_do_dia.descricaohumor)

        # Adiciona a descrição limpa para uso no template de hoje
        humor_do_dia.descricao_usuario_original = descricao_usuario_original
        
        # B. Lógica de rotação: Tenta carregar a dica salva (Persistência Visual)
        if dica_id_salva:
            try:
                dica_do_dia = Dicas.objects.get(pk=dica_id_salva)
            except Dicas.DoesNotExist:
                # Dica não existe mais, prossegue para a lógica de rotação (C)
                dica_id_salva = None # Reseta o ID salvo
                pass 
        
        # C. Se não há dica salva ou a dica salva foi deletada, faz a rotação (Lógica do Cache de Sessão)
        if not dica_do_dia:
            session_key = f'dicas_vistas_para_humor_{humor_tipo_id}'
            dicas_vistas = request.session.get(session_key, [])
            
            # Tenta pegar uma dica nova (excluindo as vistas na sessão)
            dicas_disponiveis = Dicas.objects.filter(
                humor_relacionado__pk=humor_tipo_id 
            ).exclude(pk__in=dicas_vistas).order_by('?') 
            
            if dicas_disponiveis.exists():
                dica_do_dia = dicas_disponiveis.first()
                dicas_vistas.append(dica_do_dia.pk)
                # Atualiza a lista de vistas na sessão
                request.session[session_key] = dicas_vistas 
            else:
                # Reinicia a rotação se todas as dicas foram vistas
                if Dicas.objects.filter(humor_relacionado__pk=humor_tipo_id).exists():
                    request.session[session_key] = [] 
                    
                    # Pega a primeira dica após o reset de sessão
                    dica_do_dia = Dicas.objects.filter(humor_relacionado__pk=humor_tipo_id).order_by('?').first() 
                    
                    if dica_do_dia:
                        request.session[session_key] = [dica_do_dia.pk] # Adiciona a primeira dica
                # Se não houver dicas disponíveis para esse humor, dica_do_dia permanece None
            
        # D. Persistência Final (Salva o ID da NOVA dica no banco de dados)
        # Isso acontece se dica_do_dia foi encontrada na rotação (C) E não estava salva antes (not dica_id_salva)
        if dica_do_dia and not dica_id_salva: 
            # Novo valor do descricaohumor: [DICA ID:X] + descrição original do usuário
            novo_desc = rebuild_descricaohumor(dica_do_dia.pk, descricao_usuario_original)
            
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
        
        # Extrai a dica salva e a descrição do usuário (USANDO FUNÇÃO AUXILIAR)
        dica_registro_id, desc_original_reg = extract_dica_info(registro.descricaohumor)
        
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
        'humores_disponiveis': tipos_de_humor,
        'dica_do_dia': dica_do_dia, 
    }
    return render(request, 'app_LyfeSync/autocuidado/humor.html', context)
    
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
                # após o registro, quando a página é carregada, para acionar a rotação.
                humor_obj.save()
                messages.success(request, 'Seu humor foi registrado com sucesso! 😊')
                return redirect('humor')
            except IntegrityError: # Adicionado IntegrityError para tratar duplicidade (usuário/data)
                messages.error(request, f'Erro ao salvar: Você já registrou um humor para esta data, ou houve um erro de validação.')
            except Exception as e: 
                messages.error(request, f'Erro ao salvar o humor: {e}')
        else:
            messages.error(request, 'Houve um erro ao registrar o humor. Verifique os campos.')
    else:
        form = HumorForm(initial={'data': timezone.localdate()})
        
    context = {
        'form': form,
        'humores_disponiveis': humores_disponiveis 
    }
    return render(request, 'app_LyfeSync/autocuidado/registrarHumor.html', context)

@login_required(login_url='login')
def alterar_humor(request, humor_id):
    """Permite alterar um registro de Humor existente."""
    
    # 1. Busca a instância do Humor
    instance = get_object_or_404(Humor, pk=humor_id, usuario=request.user)
    
    # Guarda o ID do estado antigo ANTES do POST
    old_estado_pk = instance.estado.pk if instance.estado else None
    
    # Pré-processamento: Limpa a descrição, mas guarda o ID da dica existente
    dica_id_existente, desc_original_limpa = extract_dica_info(instance.descricaohumor)

    if request.method == 'POST':
        form = HumorForm(request.POST, instance=instance)
        
        if form.is_valid():
            humor_obj = form.save(commit=False)
            
            # CRÍTICO: VERIFICA SE O TIPO DE HUMOR MUDOU!
            new_estado_pk = form.cleaned_data['estado'].pk 
            
            if old_estado_pk != new_estado_pk:
                # Se o tipo de humor mudou, zera a dica existente para FORÇAR a rotação na view principal.
                dica_id_existente = None 
                
            nova_descricao_usuario = form.cleaned_data.get('descricaohumor', '') 
            
            # Reconstroi o campo descricaohumor, com o novo (ou antigo/zerado) dica_id_existente
            # A descrição limpa vem do form, e o ID da dica é reinserido ou removido.
            humor_obj.descricaohumor = rebuild_descricaohumor(dica_id_existente, nova_descricao_usuario)

            humor_obj.save() 
            
            messages.success(request, 'Humor alterado com sucesso! 🎉')
            return redirect('humor')
            
        else:
            messages.error(request, 'Erro na validação do formulário. Verifique os campos.')
    else:
        # Se GET, inicializa o form com a descrição limpa (apenas o texto do usuário)
        initial_data = {'descricaohumor': desc_original_limpa}
        form = HumorForm(instance=instance, initial=initial_data)
        
    context = {
        'form': form,
        'humores_disponiveis': HumorTipo.objects.all(), 
        'humor_id': humor_id, 
        'humor_atual': instance,
    }
    
    return render(request, 'app_LyfeSync/autocuidado/alterarHumor.html', context)

@require_POST
@login_required(login_url='login')
def delete_humor(request, humor_id):
    """Exclui um registro de Humor específico (via POST) e redireciona com mensagem."""
    try:
        # Garante que o usuário só exclua o seu próprio humor.
        humor_instance = get_object_or_404(Humor, pk=humor_id, usuario=request.user)
        humor_data = humor_instance.data.strftime('%d/%m/%Y')
        humor_instance.delete()
        
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
        # Busca o registro de humor
        humor_registro = Humor.objects.select_related('estado').get(usuario=request.user, data=selected_date)
        
        # Limpar a descrição removendo a tag [DICA ID:X] (USANDO FUNÇÃO AUXILIAR)
        _, cleaned_descricao = extract_dica_info(humor_registro.descricaohumor)
        
        data = {
            'exists': True,
            'id': humor_registro.pk, 
            'estado_id': humor_registro.estado.pk,
            'nome_humor': humor_registro.estado.estado, 
            'icone_path': humor_registro.estado.icone, 
            'descricaohumor': cleaned_descricao, 
        }
        return JsonResponse(data)
        
    except Humor.DoesNotExist:
        return JsonResponse({'exists': False, 'message': 'Nenhum registro encontrado'})
        
    except Exception as e:
        print(f"Erro ao carregar humor no servidor: {e}")
        return JsonResponse({'exists': False, 'error': 'Erro interno do servidor ao buscar humor.'}, status=500)

# -------------------------------------------------------------------
# VIEWS DE DICAS (APENAS REGISTRO - STAFF/ADMIN)
# -------------------------------------------------------------------

@login_required(login_url='login')
@user_passes_test(is_staff_user, login_url='/') # Restringe o acesso a usuários Staff/Admin.
def registrar_dica(request):
    """Permite registrar uma nova dica e lista as existentes (Admin/Staff)."""
    
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
    
    try:
        humores_disponiveis = HumorTipo.objects.all().order_by('pk') 
        dicas_list = Dicas.objects.all().order_by('-data_criacao')
    except NameError:
        # Fallback se os Models não estiverem disponíveis (usando mocks)
        humores_disponiveis = []
        dicas_list = []

    humor_map = get_humor_map() 
    
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
    
    dica = get_object_or_404(Dicas, pk=dica_id)
    
    if request.method == 'POST':
        form = DicasForm(request.POST, instance=dica)
        if form.is_valid():
            form.save()
            messages.success(request, f"Dica '{dica.nomeDica}' alterada com sucesso!")
            return redirect('registrar_dica') 
        else:
            messages.error(request, "Erro ao alterar a dica. Verifique os campos.")
            # Se a validação falhar no POST, é melhor redirecionar ou re-renderizar o modal na página principal,
            # mas manteremos o redirecionamento simples para a lista de gestão de dicas.
            return redirect('registrar_dica') 
            
    # Se for GET, simplesmente redireciona, pois esta view é para POST
    return redirect('registrar_dica')

@login_required(login_url='login')
@user_passes_test(is_staff_user, login_url='/') 
def excluir_dica(request, dica_id):
    """Permite excluir uma dica existente (Staff/Admin) via POST."""
    
    dica = get_object_or_404(Dicas, pk=dica_id)
    
    if request.method == 'POST':
        try:
            dica_nome = dica.nomeDica
            dica.delete()
            messages.success(request, f"Dica '{dica_nome}' excluída com sucesso.")
        except Exception as e:
            messages.error(request, f"Erro ao excluir a dica: {e}")
            
        return redirect('registrar_dica')
    
    # Se for GET, redireciona para evitar acesso direto
    return redirect('registrar_dica')

# -------------------------------------------------------------------
# VIEWS DE GRATIDÃO (CRUD e Listagem)
# -------------------------------------------------------------------

MAX_GRATITUDE_LIST_COUNT = 60 # Limite total de gratidões na listagem
GRATITUDE_PER_PAGE = 15 # Gratidões por página

@login_required
def gratidao(request):
    """
    Exibe o Diário de Gratidão, lida com a exibição de gratidões do dia
    e lista as gratidões antigas com paginação.
    """
    usuario = request.user
    hoje = date.today()
    
    # 1. Buscar Gratidões do Dia Atual (em destaque)
    # Ordena para garantir que, se houver mais de 3, as 3 primeiras apareçam.
    gratidoes_hoje = Gratidao.objects.filter(usuario=usuario, data=hoje).order_by('idgratidao')[:3]
    
    # 2. Configurar o Formulário de Inclusão
    if gratidoes_hoje.exists():
        # Se houver gratidões de hoje, sugere o formulário de Inclusão Tardia (com data de ontem)
        create_form = GratidaoCreateForm(initial={'data': hoje - timedelta(days=1)})
    else:
        # Se não houver, sugere o formulário de Inclusão de Hoje (com data de hoje)
        create_form = GratidaoCreateForm(initial={'data': hoje})
    
    # 3. Listagem Paginada de Gratidões Antigas (Max 60, excluindo as de hoje)
    
    todas_gratidoes = Gratidao.objects.filter(usuario=usuario).exclude(data=hoje).order_by('-data', '-idgratidao')[:MAX_GRATITUDE_LIST_COUNT]

    # Paginação
    paginator = Paginator(todas_gratidoes, GRATITUDE_PER_PAGE)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Formulário de Update vazio (será preenchido via JS no modal)
    update_form = GratidaoUpdateForm()

    context = {
        'hoje': hoje,
        'gratidoes_hoje': gratidoes_hoje,  # Gratidões em destaque no topo
        'create_form': create_form,       # Form para Inclusão (Hoje ou Tardia)
        'update_form': update_form,       # Form para Alteração
        'page_obj': page_obj,             # Lista paginada de gratidões antigas
    }
    
    return render(request, 'app_LyfeSync/autocuidado/gratidao.html', context)

@login_required
@require_POST
def registrar_gratidao(request):
    """
    Processa a criação de até 3 gratidões de uma vez.
    Utiliza o método save() do GratidaoCreateForm para criar os objetos em lote.
    """
    form = GratidaoCreateForm(request.POST)
    usuario = request.user
    
    if form.is_valid():
        try:
            gratidoes_criadas_objs = form.save(user=usuario)
            gratidoes_criadas = len(gratidoes_criadas_objs)
            data = form.cleaned_data['data'] # A data é sempre extraída do form limpo
            
            messages.success(request, f'Sucesso! {gratidoes_criadas} gratidão(ões) registrada(s) para {data.strftime("%d/%m/%Y")}.')

        except Exception as e:
            # Captura qualquer erro que possa ocorrer durante a transação ou salvamento.
            messages.error(request, f'Ocorreu um erro ao salvar as gratidões: {e}. Tente novamente.')
            
    else:
        # Erros de validação
        messages.error(request, 'Erro: O formulário contém erros. Verifique os campos e tente novamente.')

    return redirect(reverse('gratidao'))

@login_required
def alterar_gratidao(request, pk):
    """
    Processa a alteração de uma única gratidão
    """
    gratidao_obj = get_object_or_404(Gratidao, idgratidao=pk, usuario=request.user)
    
    if request.method == 'POST':
        form = GratidaoUpdateForm(request.POST, instance=gratidao_obj)
        
        if form.is_valid():
            try:
                # 1. Salva o objeto na memória sem fazer commit no banco (apenas atualiza o campo descricaogratidao)
                gratidao_instance = form.save(commit=False)
                new_description = form.cleaned_data['descricaogratidao']
                
                # 2. Lógica para regenerar o nome/título curto (usando os primeiros caracteres da primeira linha)
                first_line = new_description.split('\n')[0].strip()
                name = re.sub(r'\s+', ' ', first_line) # Remove múltiplos espaços
                
                if len(name) > 100:
                    name = name[:97].strip() + '...'
                                
                # 4. Salva a instância no banco de dados
                gratidao_instance.save() 
                
                # CORREÇÃO 2: Usa a variável 'name' (o título curto gerado) na mensagem de sucesso,
                # em vez da descrição completa, que seria muito longa.
                messages.success(request, f'Gratidão "{name}" alterada com sucesso!')
            
            except Exception as e:
                messages.error(request, f'Erro ao alterar a gratidão: {e}')
        else:
            messages.error(request, 'Erro na alteração: Os dados fornecidos são inválidos.')
            # Adiciona o erro do formulário para garantir que a mensagem de erro seja vista
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'Erro no campo {field}: {error}')
            
    return redirect(reverse('gratidao'))

@login_required
@require_POST
def delete_gratidao(request, pk):
    """
    Processa a exclusão de uma gratidão específica.
    """
    gratidao_obj = get_object_or_404(Gratidao, idgratidao=pk, usuario=request.user)
    
    try:
        # CORREÇÃO 3: Recupera o título/nome curto antes de deletar para usá-lo na mensagem
        # Assumindo que você ainda está gerando o nome curto a partir da descrição para fins de feedback.
        first_line = gratidao_obj.descricaogratidao.split('\n')[0].strip()
        name_for_feedback = re.sub(r'\s+', ' ', first_line)
        if len(name_for_feedback) > 100:
            name_for_feedback = name_for_feedback[:97].strip() + '...'
            
        gratidao_obj.delete()
        # Usa a variável 'name_for_feedback' corrigida na mensagem de sucesso
        messages.success(request, f'Gratidão "{name_for_feedback}" excluída com sucesso.')
        
    except Exception as e:
        messages.error(request, f'Erro ao excluir a gratidão: {e}')

    return redirect(reverse('gratidao'))

# -------------------------------------------------------------------
# VIEWS DE AFIRMAÇÃO (CRUD e Listagem)
# -------------------------------------------------------------------

# Constantes para Paginação
AFIRMACOES_POR_PAGINA = 15 

@login_required
def afirmacao(request):
    """
    Página principal de afirmações, exibe o histórico e os modais.
    """
    user = request.user
    
    # 1. Obter e Paginar o Histórico de Afirmações
    # Ordenar por data (mais recente primeiro) e depois por ID (para estabilidade)
    historico = Afirmacao.objects.filter(usuario=user).order_by('-data', '-idafirmacao')
    
    paginator = Paginator(historico, AFIRMACOES_POR_PAGINA)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # 2. Formulários para Modais
    registro_form = AfirmacaoRegistroForm()
    alteracao_form = AfirmacaoAlteracaoForm()
    
    context = {
        'page_obj': page_obj,
        'registro_form': registro_form,
        'alteracao_form': alteracao_form,
        # Variáveis úteis para o template
        'hoje': date.today().strftime('%Y-%m-%d'),
        'css_base_class': 'autocuidado', # Classe base para o CSS
    }
    
    return render(request, 'app_LyfeSync/autocuidado/afirmacao.html', context)

@login_required
def registrar_afirmacao(request):
    """
    Processa a inclusão de 1 a 3 afirmações positivas por dia.
    """
    if request.method == 'POST':
        form = AfirmacaoRegistroForm(request.POST)
        if form.is_valid():
            afirmacoes_para_salvar = []
            user = request.user
            data = form.cleaned_data['data']
            
            # Campos de descrição
            descricoes = [
                form.cleaned_data.get('descricao_1'),
                form.cleaned_data.get('descricao_2'),
                form.cleaned_data.get('descricao_3')
            ]
            
            # Filtrar descrições vazias (apenas as que o usuário preencheu)
            descricoes_validas = [d for d in descricoes if d]
            
            if not descricoes_validas:
                # Embora o form.clean() deva evitar isso, é um bom fallback
                messages.error(request, 'Pelo menos uma afirmação é obrigatória.')
                return redirect('afirmacao')

            try:
                # Usar transação para garantir que todas ou nenhuma sejam salvas
                with transaction.atomic():
                    for descricao in descricoes_validas:
                        afirmacoes_para_salvar.append(
                            Afirmacao(
                                usuario=user,
                                data=data,
                                descricaoafirmacao=descricao
                            )
                        )
                    
                    Afirmacao.objects.bulk_create(afirmacoes_para_salvar)
                    
                    messages.success(request, f'{len(descricoes_validas)} Afirmação(ões) registrada(s) com sucesso para o dia {data.strftime("%d/%m/%Y")}!')
            
            except Exception as e:
                messages.error(request, f'Erro ao registrar afirmação(ões): {e}')
                
        else:
            # Mensagem de erro de validação do formulário
            messages.error(request, 'Erro de validação no formulário de registro. Verifique a data e os campos.')
    
    # Redireciona sempre para a página principal (afirmacao) após o processamento
    return redirect('afirmacao')

@login_required
def alterar_afirmacao(request, afirmacao_id):
    """
    Processa a alteração de uma afirmação individual.
    """
    afirmacao_obj = get_object_or_404(Afirmacao, pk=afirmacao_id, usuario=request.user)
    
    if request.method == 'POST':
        # Nota: Usamos AfirmacaoAlteracaoForm que tem apenas um campo de texto.
        form = AfirmacaoAlteracaoForm(request.POST) 
        
        if form.is_valid():
            try:
                nova_descricao = form.cleaned_data['descricaoafirmacao']
                # Atualiza apenas o campo de descrição
                afirmacao_obj.descricaoafirmacao = nova_descricao
                afirmacao_obj.save()
                
                messages.success(request, f'Afirmação do dia {afirmacao_obj.data.strftime("%d/%m/%Y")} alterada com sucesso!')
            
            except Exception as e:
                messages.error(request, f'Erro ao alterar a afirmação: {e}')
        
        else:
            # Mensagem de erro de validação
            messages.error(request, 'Erro de validação ao alterar afirmação. A descrição não pode ser vazia.')
            
    # Redireciona sempre
    return redirect('afirmacao')


@login_required
def delete_afirmacao(request, afirmacao_id):
    """
    Processa a exclusão de uma afirmação individual.
    """
    afirmacao_obj = get_object_or_404(Afirmacao, pk=afirmacao_id, usuario=request.user)
    
    if request.method == 'POST':
        data_registro = afirmacao_obj.data.strftime("%d/%m/%Y")
        try:
            afirmacao_obj.delete()
            messages.success(request, f'Afirmação do dia {data_registro} excluída com sucesso.')
        except Exception as e:
            messages.error(request, f'Erro ao excluir a afirmação: {e}')
            
    # Redireciona sempre
    return redirect('afirmacao')