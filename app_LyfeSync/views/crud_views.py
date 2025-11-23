# app_LyfeSync/views/crud_views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.contrib.auth.decorators import login_required, user_passes_test
from django.utils import timezone
from datetime import timedelta
import locale
import re
from django.views.decorators.http import require_POST
from django.template.loader import render_to_string 
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.forms.models import modelformset_factory
from django.db import IntegrityError # Importação adicional para melhor tratamento de erro

# -------------------------------------------------------------------
# IMPORTAÇÕES DE MOCKS/FUNÇÕES AUXILIARES (Design para Portabilidade)
# -------------------------------------------------------------------

try:
    # Tenta importar mocks se estiver em um ambiente de exportação/teste
    from ._aux_logic import Gratidao, Afirmacao, Humor, HumorTipo, Dicas, Habito, StatusDiario, MockUser, GratidaoForm, AfirmacaoForm, HumorForm, DicasForm, get_humor_map, extract_dica_info, rebuild_descricaohumor, extract_dica_gratidao_info, rebuild_descricaogratidao
except ImportError:
    # Se falhar, importa os modelos e forms reais do Django
    from ..forms import GratidaoForm, AfirmacaoForm, HumorForm, DicasForm
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

    # Manter as stubs para Gratidão, mesmo que não estejam sendo usadas para a tag no momento.
    def extract_dica_gratidao_info(desc): return None, desc
    def rebuild_descricaogratidao(dica_id, desc): return desc
    
    # MockUser de fallback para contexto (apesar de não ser usado nas views decoradas)
    class MockUser:
        def __init__(self, username="mock_user"): self.username = username
        @property
        def is_authenticated(self): return True


# -------------------------------------------------------------------
# CONFIGURAÇÃO DE LOCALE
# -------------------------------------------------------------------

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

# --- REGRAS DE PAGINAÇÃO ---
REGISTROS_POR_PAGINA = 15

@login_required(login_url='login')
def gratidao(request):
    """
    View principal que lida com:
    1. CRUD diário (via ModelFormSet, máximo de 3 gratidões por dia).
    2. Listagem paginada do histórico.
    3. Destaque da gratidão mais recente do dia.
    """
    # 1. AUTENTICAÇÃO E DATA (CORREÇÃO: Removemos a lógica do MockUser, pois @login_required garante request.user)
    usuario = request.user
    data_hoje = timezone.localdate()

    # QuerySet de todas as gratidões do usuário (para paginação)
    todas_gratidoes_qs = Gratidao.objects.filter(
        usuario=usuario
    ).order_by('-data', '-idgratidao')

    # QuerySet das gratidões do dia
    gratidao_do_dia_qs = todas_gratidoes_qs.filter(data=data_hoje)

    # Destaque (a mais recente do dia, se houver)
    gratidao_do_dia_destaque = gratidao_do_dia_qs.first()

    # 2. Definição Dinâmica do FormSet
    GratidaoFormSet = modelformset_factory(
        Gratidao,
        form=GratidaoForm,
        extra=max(0, 3 - gratidao_do_dia_qs.count()), # Adiciona o necessário para chegar a 3 (min 0)
        max_num=3,
        can_delete=False
    )

    formset = None

    if request.method == 'POST':
        # Instancia o FormSet com os dados POST e o QuerySet EXISTENTE do dia
        formset = GratidaoFormSet(request.POST, queryset=gratidao_do_dia_qs) 

        if formset.is_valid():
            # Itera sobre as instâncias a serem salvas (novas ou alteradas)
            instances = formset.save(commit=False)
            
            # Garante que as novas instâncias tenham o usuário atribuído
            for instance in instances:
                if not instance.pk: 
                    instance.usuario = usuario
                instance.save()
                
            # Salva os objetos que foram marcados para exclusão (se can_delete fosse True, mas aqui não é)
            # formset.save_m2m() # Apenas se houver campos ManyToManyField no GratidaoForm

            # Mensagens de feedback
            messages.success(
                request, 'Gratidões registradas/atualizadas com sucesso! 🎉')
            return redirect('gratidao')
        else:
            # Erro de validação. O formset com erros será passado para o template.
            messages.error(
                request, 'Houve um erro ao registrar sua gratidão. Verifique os campos e se o formulário está preenchido corretamente.')

    # Se GET ou POST com erro, inicializa o formset com os dados do dia
    if formset is None:
        formset = GratidaoFormSet(queryset=gratidao_do_dia_qs)
        
    # 3. PAGINAÇÃO DO HISTÓRICO
    gratidoes_para_paginar = todas_gratidoes_qs

    paginator = Paginator(gratidoes_para_paginar, REGISTROS_POR_PAGINA)
    page_number = request.GET.get('page', 1)

    try:
        gratidoes_paginadas = paginator.page(page_number)
    except PageNotAnInteger:
        gratidoes_paginadas = paginator.page(1)
    except EmptyPage:
        gratidoes_paginadas = paginator.page(paginator.num_pages)

    # 4. Contexto e Renderização
    data_hoje_local = timezone.localdate()
    try:
        # Tenta formatar o nome do mês em português
        mes_atual_extenso = data_hoje_local.strftime('%B').capitalize()
    except:
        # Fallback se o locale falhar
        mes_atual_extenso = data_hoje_local.strftime('%B')

    context = {
        'gratidao_do_dia': gratidao_do_dia_qs, 
        'gratidao_do_dia_destaque': gratidao_do_dia_destaque,
        'gratidoes_paginadas': gratidoes_paginadas,
        'mes_atual': mes_atual_extenso,
        'ano_atual': data_hoje.year,
        'formset': formset,
    }

    return render(request, 'app_LyfeSync/autocuidado/gratidao.html', context)


@login_required(login_url='login')
def registrar_gratidao(request):
    """
    Processa a inclusão de novas gratidões (múltiplas, até 3) em qualquer data
    escolhida pelo usuário no modal de inclusão.
    """
    usuario = request.user
    
    # 1. Definição do FormSet para CRIAÇÃO
    GratidaoFormSet = modelformset_factory(
        Gratidao,
        form=GratidaoForm,
        extra=3, 
        max_num=3,
        can_delete=False
    )

    if request.method == 'POST':
        # Instanciamos o formset SEM um queryset, garantindo que será sempre uma CRIAÇÃO
        formset = GratidaoFormSet(request.POST) 

        if formset.is_valid():
            
            instances = formset.save(commit=False)
            
            registros_criados = 0
            # formset.new_objects contém apenas os objetos criados (forms com dados)
            for instance in formset.new_objects:
                # O ModelFormSet cuida de forms vazios; aqui só precisamos garantir o usuário e salvar.
                instance.usuario = usuario
                instance.save()
                registros_criados += 1

            if registros_criados > 0:
                messages.success(
                    request, f'{registros_criados} gratidão(ões) registrada(s) com sucesso! 😊')
            else:
                messages.info(request, 'Nenhuma gratidão preenchida para salvar.')
                    
            return redirect('gratidao')
        else:
            # Se o formset não for válido, exibe as mensagens de erro
            messages.error(
                request, 'Houve um erro ao registrar sua gratidão. Verifique se a data e o conteúdo foram preenchidos corretamente.')
            return redirect('gratidao')

    # Se for GET, simplesmente redireciona, pois esta view é apenas para POST do modal.
    return redirect('gratidao')


@login_required(login_url='login')
def alterar_gratidao(request, gratidao_id):
    """Permite alterar um registro de gratidão existente (tipicamente via modal)."""
    usuario = request.user

    # Busca a instância da gratidão, garantindo que pertence ao usuário logado
    gratidao_instance = get_object_or_404(
        Gratidao, pk=gratidao_id, usuario=usuario) 

    if request.method == 'POST':
        form = GratidaoForm(request.POST, instance=gratidao_instance)

        if form.is_valid():
            form.save()
            messages.success(request, 'Gratidão alterada com sucesso! ❤️')
            return redirect('gratidao')
        else:
            messages.error(
                request, 'Falha na alteração da gratidão. Verifique os dados.')
            # Redireciona mesmo com erro para manter a simplicidade (erros são exibidos via messages)
            return redirect('gratidao')

    # Se for GET, simplesmente redireciona, pois a alteração é esperada via POST
    return redirect('gratidao')


@require_POST
@login_required(login_url='login')
def delete_gratidao(request, gratidao_id):
    """Exclui um registro de Gratidão específico (via POST)."""
    usuario = request.user

    try:
        # Garante que apenas o proprietário pode excluir
        gratidao_obj = Gratidao.objects.get(pk=gratidao_id, usuario=usuario)
    except Gratidao.DoesNotExist:
        messages.error(
            request, 'Registro não encontrado ou você não tem permissão.')
        return redirect('gratidao')

    try:
        gratidao_obj.delete()
        messages.success(
            request, 'O registro de gratidão foi excluído com sucesso! 💔')
    except Exception as e:
        messages.error(
            request, f'Erro ao excluir o registro de gratidão: {e}')

    return redirect('gratidao')

# -------------------------------------------------------------------
# VIEWS DE AFIRMAÇÃO (CRUD e Listagem)
# -------------------------------------------------------------------

@login_required(login_url='login')
def afirmacao(request):
    """Página de Afirmações. Lista as últimas afirmações do usuário."""
    
    
    ultimas_afirmacoes = Afirmacao.objects.filter(
        usuario=request.user
    ).order_by('-data')[:15]
    
    context = {
        'ultimas_afirmacoes': ultimas_afirmacoes,
    }

    return render(request, 'app_LyfeSync/afirmacao/afirmacao.html', context)


@login_required(login_url='login')
def registrar_afirmacao(request):
    """Permite registrar uma nova Afirmação e redireciona para a listagem."""
    if request.method == 'POST':
        form = AfirmacaoForm(request.POST)
        if form.is_valid():
            afirmacao_obj = form.save(commit=False)
            
            afirmacao_obj.usuario = request.user
            
            if not afirmacao_obj.data:
                afirmacao_obj.data = timezone.localdate()
                
            afirmacao_obj.save()
            messages.success(request, 'Afirmação registrada com sucesso! ✨')
            return redirect('afirmacao') 
        else:
            messages.error(request, 'Houve um erro ao registrar a afirmação. Verifique os campos.')
    else:
        form = AfirmacaoForm(initial={'data': timezone.localdate()})
        
    context = {'form': form}
    return render(request, 'app_LyfeSync/afirmacao/registrarAfirmacao.html', context)


@login_required(login_url='login')
def alterar_afirmacao(request, afirmacao_id):
    """Permite alterar uma Afirmação existente. Requer login e ID da Afirmação."""
    
    # Busca o objeto pela Primary Key (pk)
    afirmacao_instance = get_object_or_404(Afirmacao, pk=afirmacao_id, usuario=request.user) 
    
    if request.method == 'POST':
        form = AfirmacaoForm(request.POST, instance=afirmacao_instance)
        if form.is_valid():
            form.save()
            messages.success(request, 'Afirmação alterada com sucesso! ✨')
            return redirect('afirmacao') # Redireciona para a lista
        else:
            messages.error(request, 'Erro na validação do formulário. Verifique os campos.')
    else:
        form = AfirmacaoForm(instance=afirmacao_instance)
        
    context = {'form': form, 'afirmacao_id': afirmacao_id}
    return render(request, 'app_LyfeSync/afirmacao/alterarAfirmacao.html', context)


@require_POST
@login_required(login_url='login')
def delete_afirmacao(request, afirmacao_id):
    """Exclui um registro de Afirmação específico (via POST/AJAX)."""
    try:
        # Busca o objeto pela Primary Key (pk)
        afirmacao_instance = get_object_or_404(Afirmacao, pk=afirmacao_id, usuario=request.user)
        afirmacao_instance.delete()
        # Retorna sucesso para o uso via AJAX, mas usa o messages para feedback
        messages.success(request, f'Afirmação excluída com sucesso.')
        return JsonResponse({'status': 'success', 'message': f'Afirmação ID {afirmacao_id} excluída.'})
    except Exception as e:
        messages.error(request, f'Erro ao excluir a afirmação: {e}')
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)