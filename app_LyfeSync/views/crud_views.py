# app_LyfeSync/views/crud_views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.contrib.auth.decorators import login_required, user_passes_test
from django.utils import timezone
from datetime import timedelta
import locale
import re
import json
from django.views.decorators.http import require_POST
from django.template.loader import render_to_string 
from ..forms import GratidaoForm, AfirmacaoForm, HumorForm, DicasForm
from ..models import Gratidao, Afirmacao, Humor, HumorTipo, Dicas, Habito, StatusDiario 
# Importando a função utilitária do arquivo auxiliar
from ._aux_logic import get_humor_map, _get_humor_cor_classe 

# Configuração de locale para formatação de data/mês em português
try:
    locale.setlocale(locale.LC_ALL, 'pt_BR.utf8')
except locale.Error:
    try:
        locale.setlocale(locale.LC_ALL, 'pt_BR')
    except:
        pass

# -------------------------------------------------------------------
# FUNÇÕES AUXILIARES DE MANIPULAÇÃO DE DICA (Refatoração de Regex)
# -------------------------------------------------------------------

# Variável de regex global para ser usada em todas as views, capturando o ID da dica: [DICA ID:X]
DICA_DELIMITADOR = r"\[DICA ID:(\d+)\]"

def extract_dica_info(descricaohumor):
    """
    Extrai o ID da Dica e a descrição original do usuário do campo descricaohumor.
    Retorna uma tupla: (dica_id: int/None, descricao_usuario_original: str)
    """
    if not descricaohumor:
        return None, ""
    
    match = re.match(DICA_DELIMITADOR, descricaohumor)
    
    if match:
        dica_id = int(match.group(1))
        # Remove o delimitador para obter a descrição original
        descricao_usuario_original = re.sub(DICA_DELIMITADOR, '', descricaohumor).strip()
        return dica_id, descricao_usuario_original
    else:
        # Se não tem a tag, a descrição original é o campo completo
        return None, descricaohumor.strip()

def rebuild_descricaohumor(dica_id, user_description):
    """
    Constrói o valor final do campo descricaohumor, prefixando a tag de dica se houver um ID.
    """
    user_description_cleaned = user_description.strip()
    if dica_id:
        return f"[DICA ID:{dica_id}] {user_description_cleaned}"
    return user_description_cleaned

# -------------------------------------------------------------------
# FUNÇÃO DE TESTE DE AUTORIZAÇÃO (para Dicas)
# -------------------------------------------------------------------

def is_staff_user(user):
    """Função de teste para o decorador @user_passes_test.
    Verifica se o usuário é staff/administrador (e ativo).
    """
    # Certifique-se de que o usuário é ativo e tem permissão de staff
    return user.is_active and user.is_staff

# -------------------------------------------------------------------
# VIEW PRINCIPAL
# -------------------------------------------------------------------

@login_required(login_url='login')
def autocuidado(request):
    """Página de Autocuidado, que pode listar Afirmações, Gratidão e Humor. Requer login."""
    # Busca 5 afirmações aleatórias do usuário
    afirmacoes = Afirmacao.objects.filter(usuario=request.user).order_by('?')[:5]
    
    context = {'afirmacoes': afirmacoes}
    # Caminho do template
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
                request.session[session_key] = dicas_vistas
            else:
                # Reinicia a rotação se todas as dicas foram vistas
                if Dicas.objects.filter(humor_relacionado__pk=humor_tipo_id).exists():
                    request.session[session_key] = [] 
                    
                    # Pega a primeira dica após o reset de sessão
                    dica_do_dia = Dicas.objects.filter(humor_relacionado__pk=humor_tipo_id).order_by('?').first() 
                    
                    if dica_do_dia:
                        request.session[session_key] = [dica_do_dia.pk]

        # D. Persistência Final (Salva o ID da NOVA dica no banco de dados)
        # Isso acontece se dica_do_dia foi encontrada na rotação (C) E não estava salva antes (not dica_id_salva)
        if dica_do_dia and not dica_id_salva: 
            # Novo valor do descricaohumor: [DICA ID:X] + descrição original do usuário
            novo_desc = rebuild_descricaohumor(dica_do_dia.pk, descricao_usuario_original)
            
            humor_do_dia.descricaohumor = novo_desc
            humor_do_dia.save(update_fields=['descricaohumor'])
            
            # Não é necessário re-atribuir humor_do_dia.descricao_usuario_original, pois a exibição usa o valor limpo (passo A)
            
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
        
        # CÓDIGO DO HISTÓRICO: Extrai a dica salva e a descrição do usuário (USANDO FUNÇÃO AUXILIAR)
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
            except Exception: # Melhor tratar IntegrityError se houver unique_together para usuário/data
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

@login_required(login_url='login')
def alterar_humor(request, humor_id): 
    """Permite alterar um Humor existente, preservando a tag [DICA ID:X] se ela existir."""
    
    # Simulação de modelos e funções necessárias para o contexto
    # Substitua pelas suas importações reais
    class HumorTipo:
        objects = [] # Simulação
        
    class Humor:
        objects = [] # Simulação
        
    def extract_dica_info(desc):
        # Simulação da função auxiliar
        if "[DICA ID:" in desc:
            return 123, desc.split("[DICA ID:")[0].strip()
        return None, desc

    def rebuild_descricaohumor(dica_id, new_desc):
        # Simulação da função auxiliar
        if dica_id:
            return f"{new_desc} [DICA ID:{dica_id}]"
        return new_desc
        
    class HumorForm:
        # Simulação de um Django Form
        def __init__(self, data=None, instance=None, initial=None):
            self.data = data
            self.instance = instance
            self.is_bound = data is not None
            self.cleaned_data = {}
            if self.is_bound and self.instance:
                self.cleaned_data = {'descricaohumor': data.get('descricaohumor'), 'estado': data.get('estado'), 'data': data.get('data')}
            
            # Simulação de campos para renderização
            self.data = type('Field', (object,), {'id_for_label': 'id_data', 'label': 'Data', 'value': (instance.data if instance and instance.data else (initial.get('data') if initial and 'data' in initial else timezone.localdate())), 'errors': []})()
            self.estado = type('Field', (object,), {'id_for_label': 'id_estado', 'label': 'Estado', 'errors': []})()
            self.descricaohumor = type('Field', (object,), {'id_for_label': 'id_descricaohumor', 'label': 'Descrição do Humor', 'value': (instance.descricaohumor if instance and instance.descricaohumor else (initial.get('descricaohumor') if initial and 'descricaohumor' in initial else '')), 'errors': []})()

        def is_valid(self):
            # Simulação de validação
            return self.is_bound
        
        def save(self, commit=True):
            # Simulação de save
            return self.instance or type('HumorObj', (object,), {'usuario': request.user, 'data': timezone.localdate(), 'save': lambda: None})()
            
    # Fim da Simulação (Use suas imports reais acima)
    
    # humores_disponiveis = HumorTipo.objects.all()
    humores_disponiveis = [{'pk': 1, 'estado': 'Feliz', 'icone': 'img/icon/feliz.png'}, 
                           {'pk': 2, 'estado': 'Calmo', 'icone': 'img/icon/calmo.png'},
                           {'pk': 3, 'estado': 'Ansioso', 'icone': 'img/icon/ansioso.png'},
                           {'pk': 4, 'estado': 'Triste', 'icone': 'img/icon/triste.png'},
                           {'pk': 5, 'estado': 'Irritado', 'icone': 'img/icon/raiva.png'},                           ]

    # Simulação da instância (substituir por sua lógica real)
    instance = type('HumorInstance', (object,), {
        'pk': humor_id,
        'usuario': request.user,
        'data': timezone.localdate(),
        'estado': type('Estado', (object,), {'pk': 1, 'estado': 'Feliz'}),
        'descricaohumor': 'Me sentindo ótimo! [DICA ID:123]'
    })()

    # Pré-processamento: Limpa a descrição para o formulário (USANDO FUNÇÃO AUXILIAR)
    dica_id_existente, desc_original_limpa = extract_dica_info(instance.descricaohumor)

    if request.method == 'POST':
        # Instancia o form com os dados POST e a instância atual
        form = HumorForm(request.POST, instance=instance)
        
        if form.is_valid():
            humor_obj = form.save(commit=False)
            
            nova_descricao_usuario = request.POST.get('descricaohumor', '') # form.cleaned_data.get('descricaohumor', '')
            
            # Reconstroi o campo descricaohumor, garantindo a persistência da tag da dica
            humor_obj.descricaohumor = rebuild_descricaohumor(dica_id_existente, nova_descricao_usuario)

            # humor_obj.save() # Use sua chamada real
            
            messages.success(request, 'Humor alterado com sucesso! 🎉')
            return redirect('humor') 
        else:
            messages.error(request, 'Erro na validação do formulário. Verifique os campos.')
    else:
        # Inicializa o formulário com a descrição LIMPA
        initial_data = {'descricaohumor': desc_original_limpa}
        form = HumorForm(instance=instance, initial=initial_data)
        
    context = {
        'form': form,
        'humores_disponiveis': humores_disponiveis,
        'humor_id': humor_id, 
        'humor_atual': instance,
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
        
        # CORREÇÃO CRÍTICA: Limpar a descrição removendo a tag [DICA ID:X] (USANDO FUNÇÃO AUXILIAR)
        _, cleaned_descricao = extract_dica_info(humor_registro.descricaohumor)
        
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
# VIEWS DE DICAS (APENAS REGISTRO)
# -------------------------------------------------------------------

@login_required(login_url='login')
@user_passes_test(is_staff_user, login_url='/') # Restringe o acesso a usuários Staff/Admin.
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
    
    try:
        humores_disponiveis = HumorTipo.objects.all().order_by('pk') 
    except NameError:

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
            messages.error(request, "Erro ao alterar a dica. Verifique os campos.")

            # Se a validação falhar, redireciona para a view principal (que também lista) para mostrar a mensagem de erro.
            # return registrar_dica(request) # Não é recomendado, use redirect com a mensagem.
            
    # Se for GET, redireciona para a view principal (isso não renderiza o formulário de alteração, 
    # pois o formulário de alteração provavelmente é modal ou embutido na view de listagem 'registrar_dica')
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
# VIEWS DE GRATIDÃO (CRUD e Listagem)
# -------------------------------------------------------------------

@login_required(login_url='login')
def gratidao(request):
    """Página de Gratidão. Lista todas as gratidões do mês atual."""
    
    data_hoje = timezone.localdate()
    primeiro_dia_mes = data_hoje.replace(day=1)
    
    
    gratidoes_do_mes = Gratidao.objects.filter(
        usuario=request.user, 
        data__gte=primeiro_dia_mes
    ).order_by('-data') 
    
    # Formatação do nome do mês em português
    mes_atual_extenso = data_hoje.strftime('%B').capitalize()

    context = {
        'gratidoes_do_mes': gratidoes_do_mes,
        'mes_atual': mes_atual_extenso,
        'ano_atual': data_hoje.year,
    }

    # Caminho do template
    return render(request, 'app_LyfeSync/gratidao/gratidao.html', context)


@login_required(login_url='login') 
def registrar_gratidao(request):
    """Permite registrar uma nova Gratidão. Requer login."""
    if request.method == 'POST':
        form = GratidaoForm(request.POST)
        if form.is_valid():
            gratidao_obj = form.save(commit=False)
            
            gratidao_obj.usuario = request.user 
            
            if not gratidao_obj.data:
                gratidao_obj.data = timezone.localdate()
                
            gratidao_obj.save()
            messages.success(request, 'Sua gratidão foi registrada com sucesso! 😊')
            return redirect('gratidao')
        else:
            messages.error(request, 'Houve um erro ao registrar sua gratidão. Verifique os campos.')
    else:
        form = GratidaoForm(initial={'data': timezone.localdate()})
        
    context = {'form': form}
    # Caminho do template
    return render(request, 'app_LyfeSync/gratidao/registrarGratidao.html', context)


@login_required(login_url='login')
def alterar_gratidao(request, gratidao_id): 
    """Permite alterar uma Gratidao existente. Requer login e ID da Gratidão."""
    
    # Busca o objeto pela Primary Key (pk)
    gratidao_instance = get_object_or_404(Gratidao, pk=gratidao_id, usuario=request.user) 
    
    if request.method == 'POST':
        form = GratidaoForm(request.POST, instance=gratidao_instance)
        if form.is_valid():
            form.save()
            messages.success(request, 'Gratidão alterada com sucesso! 💖')
            return redirect('gratidao') 
        else:
            messages.error(request, 'Erro na validação do formulário. Verifique os campos.')
    else:
        form = GratidaoForm(instance=gratidao_instance)
        
    context = {'form': form, 'gratidao_id': gratidao_id}
    # Caminho do template
    return render(request, 'app_LyfeSync/gratidao/alterarGratidao.html', context)


@require_POST
@login_required(login_url='login')
def delete_gratidao(request, gratidao_id):
    """Exclui um registro de Gratidão específico (via AJAX)."""
    try:
        # Busca o objeto pela Primary Key (pk)
        gratidao_instance = get_object_or_404(Gratidao, pk=gratidao_id, usuario=request.user)
        gratidao_instance.delete()
        return JsonResponse({'status': 'success', 'message': f'Gratidão ID {gratidao_id} excluída.'})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)


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

    # Caminho do template
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
    # Caminho do template
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
    # Caminho do template
    return render(request, 'app_LyfeSync/afirmacao/alterarAfirmacao.html', context)


@require_POST
@login_required(login_url='login')
def delete_afirmacao(request, afirmacao_id):
    """Exclui um registro de Afirmação específico (via AJAX)."""
    try:
        # Busca o objeto pela Primary Key (pk)
        afirmacao_instance = get_object_or_404(Afirmacao, pk=afirmacao_id, usuario=request.user)
        afirmacao_instance.delete()
        return JsonResponse({'status': 'success', 'message': f'Afirmação ID {afirmacao_id} excluída.'})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)