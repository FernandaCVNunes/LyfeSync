from django.shortcuts import render, redirect, get_object_or_404
from django.core.mail import EmailMessage
from django.conf import settings
from django.contrib import messages
from django.http import HttpResponseRedirect, HttpResponse, JsonResponse
from django.urls import reverse
from django.contrib.auth.decorators import login_required, user_passes_test
# IMPORTAÇÕES DE AUTENTICAÇÃO ATUALIZADAS:
from django.contrib.auth import logout, login # Adicionado 'login'
from django.contrib.auth.forms import UserCreationForm as CadastroForm # Importação para formulário de cadastro
from django.utils import timezone
from django.db import transaction
from datetime import date
import json 
import locale 
import calendar 
from .forms import HabitoForm, GratidaoForm, AfirmacaoForm, HumorForm, DicasForm, UserUpdateForm, PerfilUsuarioForm
from .models import Dicas, Habito, Gratidao, Afirmacao, Humor, Relatorio, Usuario, StatusDiario
from django.db.models import Q 
from django.views.decorators.http import require_POST

# -------------------------------------------------------------------
# LÓGICA AUXILIAR PARA HÁBITOS
# -------------------------------------------------------------------

def _get_checked_days_for_current_month(habito_obj):
    """Busca os dias em que o hábito foi concluído no mês atual."""
    month = date.today().month
    year = date.today().year
    
    # Consulta todas as conclusões para o hábito no mês e ano atuais
    # ASSUMIDO: O campo de data em StatusDiario é 'data_conclusao'
    completions = StatusDiario.objects.filter(
        habito=habito_obj, 
        data_conclusao__year=year, 
        data_conclusao__month=month
    )
    
    # Cria o dicionário de mapa: {dia_do_mês: True}
    checked_days = {c.data_conclusao.day: True for c in completions}
    return checked_days

# -------------------------------------------------------------------
# VIEWS PÚBLICAS (Sem necessidade de login)
# -------------------------------------------------------------------

def home(request):
    """Página inicial do site."""
    return render(request, 'app_LyfeSync/home.html')

def sobre_nos(request):
    """Página sobre a equipe e missão."""
    return render(request, 'app_LyfeSync/sobreNos.html')

def contatos(request):
    """Processa e renderiza a página de contato com envio de e-mail."""
    if request.method == 'POST':
        # 1. Captura os dados do formulário
        email_remetente = request.POST.get('email')
        assunto = request.POST.get('assunto')
        mensagem = request.POST.get('mensagem')
        anexo = request.FILES.get('anexo')
        
        # 2. Define o destinatário e o corpo do e-mail
        destinatario = ['lyfesyncpt@gmail.com']
        
        corpo_email = f"Mensagem de Contato do Site LyfeSync:\n\n"
        corpo_email += f"E-mail (Identificador): {email_remetente}\n"
        corpo_email += f"Assunto: {assunto}\n\n"
        corpo_email += "Mensagem:\n"
        corpo_email += f"----------------------------------------\n"
        corpo_email += f"{mensagem}\n"
        corpo_email += f"----------------------------------------"
        
        # 3. Cria a instância do e-mail
        mail = EmailMessage(
            subject=f"[CONTATO LYFESYNC] {assunto}",
            body=corpo_email,
            from_email=settings.DEFAULT_FROM_EMAIL, 
            to=destinatario,
            reply_to=[email_remetente], 
        )
        
        # 4. Anexa o arquivo, se existir
        if anexo:
            mail.attach(anexo.name, anexo.read(), anexo.content_type)
        
        # 5. Tenta enviar o e-mail
        try:
            mail.send(fail_silently=False)
            messages.success(request, 'Mensagem enviada com sucesso! Em breve entraremos em contato.')
            return HttpResponseRedirect(reverse('contatos')) 
        except Exception as e:
            print(f"ERRO AO ENVIAR EMAIL: {e}")
            messages.error(request, f'Ocorreu um erro ao enviar a mensagem. Por favor, tente novamente mais tarde.')

    return render(request, 'app_LyfeSync/contatos.html')

def login_view(request): 
    """Página de login."""
    # Instancia um formulário de cadastro vazio para o modal, se necessário
    form_cadastro = CadastroForm()
    context = {'form_cadastro': form_cadastro} # Passa o formulário para o template, se necessário
    return render(request, 'app_LyfeSync/login.html', context) 

def cadastro(request):
    """
    Função de view para o cadastro de novos usuários.
    Esta função é o alvo do formulário POST do modal de cadastro em login.html.
    """
    if request.method == 'POST':
        # Usa o formulário de cadastro importado (UserCreationForm)
        form = CadastroForm(request.POST) 
        if form.is_valid():
            user = form.save()
            # Loga o usuário imediatamente após o registro
            login(request, user) 
            messages.success(request, f'Bem-vindo(a), {user.username}! Seu cadastro foi realizado com sucesso.')
            # Redireciona para o dashboard após o login
            return redirect('home_lyfesync') 
        else:
            # Se o formulário for inválido, redireciona para login.html 
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"Erro em {field}: {error}")
            return redirect('login') 
            
    # Se for GET, apenas redireciona para a página de login/cadastro
    return redirect('login') 

def logout_view(request):
    """Realiza o logout do usuário e redireciona para a home."""
    logout(request)
    messages.info(request, "Sessão encerrada com sucesso.")
    return redirect('home')

# -------------------------------------------------------------------
# VIEWS PRIVADAS (Necessitam de @login_required)
# -------------------------------------------------------------------

@login_required
def home_lyfesync(request):
    """Dashboard principal da aplicação para usuários logados."""
    # CORREÇÃO/IMPORTANTE: Usando 'usuario=request.user' para Habito (Consistente com a view habito)
    total_habitos = Habito.objects.filter(usuario=request.user).count()
    
    # CORREÇÃO/IMPORTANTE: Usando 'idusuario=request.user' para Afirmacao 
    ultima_afirmacao = Afirmacao.objects.filter(
        idusuario=request.user
    ).order_by('-data').first()
    
    context = {
        'total_habitos': total_habitos,
        'ultima_afirmacao': ultima_afirmacao
    }
    return render(request, 'app_LyfeSync/homeLyfesync.html', context)


@login_required
def habito(request):
    """Lista todos os hábitos do usuário e é a página principal de hábitos."""
    
    # 1. Obter lista de hábitos reais
    try:
        # CORREÇÃO: Usando 'usuario=request.user' para Habito (Assumindo que Habito tem FK 'usuario')
        habitos_reais = Habito.objects.filter(usuario=request.user).order_by('-data_inicio')
    except Exception as e:
        print(f"Erro ao buscar hábitos no DB: {e}")
        habitos_reais = [] 

    # 2. Transformação de dados (adiciona o mapa de conclusão)
    habitos_para_template = []
    for habito_obj in habitos_reais:
        # Busca o status de conclusão para o mês atual
        checked_days_map = _get_checked_days_for_current_month(habito_obj) 

        habitos_para_template.append({
            'id': habito_obj.id,
            'nome': habito_obj.nome,
            'descricao': habito_obj.descricao, 
            'frequencia': habito_obj.frequencia, 
            # CHAVE ESPERADA PELO TEMPLATE
            'completion_status': checked_days_map 
        })
        
    # 3. Contexto de datas
    try:
        # Tenta configurar o locale para Português (Brasil ou padrão)
        locale.setlocale(locale.LC_ALL, 'pt_BR.utf8') 
    except locale.Error:
        try:
            locale.setlocale(locale.LC_ALL, 'pt_BR')
        except locale.Error:
            pass # Continua sem locale se não for possível configurar
            
    month_names = [calendar.month_abbr[i].upper() for i in range(1, 13)]
    dias_do_mes = list(range(1, 32)) 
    
    context = {
        'habitos': habitos_para_template,
        'dias_do_mes': dias_do_mes,
        'mes_atual': date.today().strftime('%b').upper(),
        'mes_nomes_lista': month_names, 
    }
    
    return render(request, 'app_LyfeSync/habito.html', context)


@login_required
def marcar_habito_concluido(request, habito_id):
    """Cria ou atualiza um StatusDiario marcando um hábito como concluído."""
    if request.method == 'POST':
        try:
            # CORREÇÃO: Usando 'usuario=request.user' para Habito
            habito = get_object_or_404(Habito, pk=habito_id, usuario=request.user) 
            data_hoje = timezone.localdate()

            # Lógica de marcação StatusDiario
            status_diario, criado = StatusDiario.objects.update_or_create(
                habito=habito,
                data_conclusao=data_hoje, # Assumindo 'data_conclusao' é o campo de data
                defaults={'concluido': True}
            )
            
            if criado:
                messages.success(request, f"Parabéns! '{habito.nome}' registrado como concluído hoje.")
            else:
                messages.info(request, f"'{habito.nome}' já estava registrado como concluído hoje.")

            return redirect('habito') 
        except Exception as e:
            messages.error(request, f"Não foi possível concluir a ação: {e}")
            return redirect('habito')

    return HttpResponse(status=405) # Método não permitido se não for POST


# -------------------------------------------------------------------
# VIEWS DE API PARA HÁBITOS (Implementação ORM)
# -------------------------------------------------------------------

@login_required
def registrar_habito(request):
    """Permite registrar um novo Habito. Requer login."""
    if request.method == 'POST':
        form = HabitoForm(request.POST)
        if form.is_valid():
            # CORREÇÃO: Usando 'usuario' ao salvar para Habito
            habito = form.save(commit=False)
            habito.usuario = request.user 
            habito.save()
            return redirect('habito')
    else:
        form = HabitoForm()
        
    context = {'form': form}
    return render(request, 'app_LyfeSync/registrarHabito.html', context)

@login_required
def alterar_habito(request, habito_id):
    """Permite alterar um Habito existente. Requer login e ID do Habito."""
    # Garante que o hábito existe e pertence ao usuário logado
    # CORREÇÃO: Usando 'usuario=request.user' para Habito
    habito_instance = get_object_or_404(Habito, id=habito_id, usuario=request.user) 
    
    if request.method == 'POST':
        form = HabitoForm(request.POST, instance=habito_instance)
        if form.is_valid():
            form.save()
            return redirect('habito')
    else:
        form = HabitoForm(instance=habito_instance)
        
    context = {'form': form, 'habito_id': habito_id}
    return render(request, 'app_LyfeSync/alterarHabito.html', context)

@require_POST
def toggle_habito_day(request, habit_id, day):
    # Lógica da API para marcar/desmarcar StatusDiario
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        try:
            data = json.loads(request.body)
            action = data.get('action') # 'check' ou 'uncheck'
            
            # 1. Encontra o Hábito e verifica se pertence ao usuário
            habito = get_object_or_404(Habito, pk=habit_id, usuario=request.user)
            
            # 2. Constrói a data
            year = date.today().year
            month = date.today().month
            date_to_toggle = date(year, month, int(day))

            # 3. Lógica de toggle/Marcação
            if action == 'check':
                StatusDiario.objects.update_or_create(
                    habito=habito,
                    data_conclusao=date_to_toggle,
                    defaults={'concluido': True}
                )
            elif action == 'uncheck':
                # Remove o StatusDiario (desmarca)
                StatusDiario.objects.filter(
                    habito=habito,
                    data_conclusao=date_to_toggle
                ).delete()
            
            return JsonResponse({'status': 'success', 'habit_id': habit_id, 'day': day, 'action': action})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
    return HttpResponse(status=400)


@require_POST
def delete_habit(request, habit_id):
    try:
        habit = get_object_or_404(Habito, id=habit_id, usuario=request.user)
        habit.delete()
        return JsonResponse({'status': 'success', 'message': f'Hábito ID {habit_id} excluído.'})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)


@login_required
def autocuidado(request):
    """Página de Autocuidado, que pode listar Afirmações, Gratidão e Humor. Requer login."""
    # CORREÇÃO/IMPORTANTE: Usando 'idusuario' para Afirmacao
    afirmacoes = Afirmacao.objects.filter(idusuario=request.user).order_by('?')[:5]
    
    context = {'afirmacoes': afirmacoes}
    return render(request, 'app_LyfeSync/autocuidado.html', context)

# app_LyfeSync/views.py

# ... (imports e outras views) ...

@login_required
def humor(request):
    """Página de Humor. Requer login."""
    
    data_hoje = timezone.localdate()

    # 1. Defina o mapa de ícones e cores AQUI (FORA do 'if')
    # Mapa de ícones Font Awesome (para listagem/dashboard)
    humor_icon_class_map = {
        'Feliz': {'icon': 'fa-solid fa-face-laugh', 'color_class': 'text-feliz'},
        'Calmo': {'icon': 'fa-solid fa-face-meh', 'color_class': 'text-calmo'},
        'Ansioso': {'icon': 'fa-solid fa-face-frown-open', 'color_class': 'text-ansioso'},
        'Triste': {'icon': 'fa-solid fa-face-sad-cry', 'color_class': 'text-triste'},
        'Irritado': {'icon': 'fa-solid fa-face-angry', 'color_class': 'text-irritado'},
    }

    try:
        humor_do_dia = Humor.objects.get(
            idusuario=request.user, 
            data=data_hoje
        )
    except Humor.DoesNotExist:
        humor_do_dia = None

    if humor_do_dia:
        # 2. Apenas a lógica de atribuição é mantida dentro do 'if'
        humor_info = humor_icon_class_map.get(humor_do_dia.estado, {'icon': 'fa-solid fa-face-question', 'color_class': ''})
        humor_do_dia.icon_class = humor_info['icon']
        humor_do_dia.color_class = humor_info['color_class']

    # 3. O dicionário 'context' é criado no final
    context = {
        'humor_do_dia': humor_do_dia,
        # O mapa agora é sempre passado para o template 'humor.html'
        'humor_icon_class_map': humor_icon_class_map 
    }
    return render(request, 'app_LyfeSync/humor.html', context)

@login_required
def gratidao(request):
    """Página de Gratidão. Lista os registros do mês atual. Requer login."""
    
    data_hoje = timezone.localdate()
    primeiro_dia_mes = data_hoje.replace(day=1)
    
    # CORREÇÃO/IMPORTANTE: Usando 'idusuario' para Gratidao
    gratidoes_do_mes = Gratidao.objects.filter(
        idusuario=request.user, 
        data__gte=primeiro_dia_mes
    ).order_by('-data') 
    
    # Lógica de Locale (mantida como estava)
    try:
        locale.setlocale(locale.LC_ALL, 'pt_BR.utf8')
    except locale.Error:
        try:
            locale.setlocale(locale.LC_ALL, 'pt_BR')
        except:
            pass
            
    mes_atual_extenso = data_hoje.strftime('%B').capitalize()

    context = {
        'gratidoes_do_mes': gratidoes_do_mes,
        'mes_atual': mes_atual_extenso,
        'ano_atual': data_hoje.year,
    }

    return render(request, 'app_LyfeSync/gratidao.html', context)

@login_required
def afirmacao(request):
    """Página de Afirmações. Lista as últimas 15 afirmações. Requer login."""
    
    # CORREÇÃO/IMPORTANTE: Usando 'idusuario' para Afirmacao
    ultimas_afirmacoes = Afirmacao.objects.filter(
        idusuario=request.user
    ).order_by('-data')[:15]
    
    context = {
        'ultimas_afirmacoes': ultimas_afirmacoes,
    }

    return render(request, 'app_LyfeSync/afirmacao.html', context)


# --- Views de Registro/Alteração (POST/SAVE) ---

@login_required
def registrar_humor(request):
    """Permite registrar um novo Humor. Requer login."""
    # MAPA DE CAMINHOS DE IMAGEM (para o formulário de seleção)
    humor_icon_class_map = {
        'Feliz': 'img/icon/feliz.png',
        'Calmo': 'img/icon/calmo.png',
        'Ansioso': 'img/icon/ansioso.png',
        'Triste': 'img/icon/triste.png',
        'Irritado': 'img/icon/raiva.png',
    }
    
    if request.method == 'POST':
        form = HumorForm(request.POST)
        if form.is_valid():
            humor_obj = form.save(commit=False)
            humor_obj.idusuario = request.user 
            
            if not humor_obj.data:
                humor_obj.data = timezone.localdate()
                
            try:
                # O save pode falhar se houver uma restrição de unicidade (data + idusuario)
                humor_obj.save()
                messages.success(request, 'Seu humor foi registrado com sucesso! 😊')
                return redirect('humor')
            except Exception as e:
                # Trata a exceção de registro duplicado
                messages.error(request, f'Erro ao salvar: Você já registrou um humor para esta data. Detalhe: {e}')
        else:
            messages.error(request, 'Houve um erro ao registrar o humor. Verifique os campos.')
    else:
        form = HumorForm()
        
    context = {
        'form': form,
        'humor_icon_class_map': humor_icon_class_map # Passa o mapa para o template
    }
    return render(request, 'app_LyfeSync/registrarHumor.html', context)

@login_required
def alterar_humor(request):
    # A view de alteração precisa da lógica de formulário (GET e POST)
    # Recomendo implementar a busca do Humor do Dia para alteração
    messages.info(request, "Lógica completa de Alterar Humor pendente de implementação.")
    return render(request, 'app_LyfeSync/alterarHumor.html')

@login_required 
def registrar_gratidao(request):
    """Permite registrar uma nova Gratidão. Requer login."""
    if request.method == 'POST':
        form = GratidaoForm(request.POST)
        if form.is_valid():
            gratidao_obj = form.save(commit=False)
            # CORREÇÃO/IMPORTANTE: Usando 'idusuario' ao salvar para Gratidao
            gratidao_obj.idusuario = request.user 
            
            if not gratidao_obj.data:
                gratidao_obj.data = timezone.localdate()
                
            gratidao_obj.save()
            messages.success(request, 'Sua gratidão foi registrada com sucesso! 😊')
            return redirect('gratidao')
        else:
            messages.error(request, 'Houve um erro ao registrar sua gratidão. Verifique os campos.')
    else:
        form = GratidaoForm()
        
    context = {'form': form}
    return render(request, 'app_LyfeSync/registrarGratidao.html', context)

@login_required
def alterar_gratidao(request):
    # A view de alteração precisa de lógica de formulário (GET e POST)
    messages.info(request, "Lógica completa de Alterar Gratidão pendente de implementação.")
    return render(request, 'app_LyfeSync/alterarGratidao.html')

@login_required
def registrar_afirmacao(request):
    """Permite registrar uma nova Afirmação e redireciona para a listagem."""
    if request.method == 'POST':
        form = AfirmacaoForm(request.POST)
        if form.is_valid():
            afirmacao_obj = form.save(commit=False)
            # CORREÇÃO/IMPORTANTE: Usando 'idusuario' ao salvar para Afirmacao
            afirmacao_obj.idusuario = request.user
            
            if not afirmacao_obj.data:
                afirmacao_obj.data = timezone.localdate()
                
            afirmacao_obj.save()
            messages.success(request, 'Afirmação registrada com sucesso! ✨')
            return redirect('afirmacao') 
        else:
            messages.error(request, 'Houve um erro ao registrar a afirmação. Verifique os campos.')
    else:
        form = AfirmacaoForm()
        
    context = {'form': form}
    return render(request, 'app_LyfeSync/registrarAfirmacao.html', context)

@login_required
def alterar_afirmacao(request):
    # A view de alteração precisa de lógica de formulário (GET e POST)
    messages.info(request, "Lógica completa de Alterar Afirmação pendente de implementação.")
    return render(request, 'app_LyfeSync/alterarAfirmacao.html')

# --- Views de Relatórios e Conta ---

@login_required
def relatorios(request):
    return render(request, 'app_LyfeSync/relatorios.html')

@login_required
def relatorio_habito(request):
    return render(request, 'app_LyfeSync/relatorioHabito.html')

@login_required
def relatorio_humor(request):
    return render(request, 'app_LyfeSync/relatorioHumor.html')

@login_required
def relatorio_gratidao(request):
    return render(request, 'app_LyfeSync/relatorioGratidao.html')

@login_required
def relatorio_afirmacao(request):
    return render(request, 'app_LyfeSync/relatorioAfirmacao.html')

@login_required
def conta(request): 
    # Esta view é renderizada por 'configuracoes_conta' agora, mas mantemos a URL caso seja um atalho simples
    return redirect('configuracoes_conta')

# Função de teste para verificar se o usuário é superusuário (Admin)
def is_superuser(user):
    return user.is_active and user.is_superuser

@login_required(login_url='login') # Redireciona para login se não estiver logado
@user_passes_test(is_superuser, login_url='home') # Redireciona para home se não for admin
def registrar_dica(request):

    if request.method == 'POST':
        form = DicasForm(request.POST)
        if form.is_valid():
            dica = form.save(commit=False)
            dica.criado_por = request.user
            dica.save()
            messages.success(request, 'Dica cadastrada com sucesso!')
            return redirect('registrar_dica') 
        else:
            messages.error(request, 'Erro ao cadastrar a dica. Verifique os campos.')
    else:
        form = DicasForm()
        
    context = {
        'form': form,
    }
    return render(request, 'app_LyfeSync/dicas.html', context)

@login_required(login_url='login')
def configuracoes_conta(request):
    # Tenta obter ou criar o perfil do usuário de forma segura
    # Assumimos que o modelo 'Usuario' é o modelo de Perfil de Usuário
    try:
        # Tenta obter o objeto 'Usuario' associado ao User.
        perfil_instance = request.user.usuario 
    except Usuario.DoesNotExist:
        # Se não existir, cria uma instância não salva para preencher o formulário GET
        perfil_instance = Usuario(user=request.user)
    
    user_form = UserUpdateForm(instance=request.user)
    perfil_form = PerfilUsuarioForm(instance=perfil_instance)
    is_admin = request.user.is_superuser

    if request.method == 'POST':
        # Instanciamos com os dados do POST
        user_form = UserUpdateForm(request.POST, instance=request.user)
        
        # O formulário de perfil é instanciado com POST
        # Se for um novo perfil, ele ainda usa a 'perfil_instance' não salva como base
        perfil_form = PerfilUsuarioForm(request.POST, instance=perfil_instance)
        
        # Inicia a transação para garantir que ambos salvem ou nenhum salve
        with transaction.atomic():
            forms_valid = True

            # Processa o formulário do usuário
            if user_form.is_valid():
                user_form.save()
            else:
                forms_valid = False
                
            # Processa o formulário de perfil
            if perfil_form.is_valid():
                perfil_obj = perfil_form.save(commit=False)
                # Garante que o FK para o User está setado corretamente
                perfil_obj.user = request.user 
                perfil_obj.save() # Salva o perfil (novo ou atualizado)
            else:
                # O perfil não é válido
                forms_valid = False 

            if forms_valid:
                messages.success(request, 'Suas configurações foram atualizadas com sucesso!')
                # Recarrega a página com o novo objeto salvo (redirect)
                return redirect('configuracoes_conta') 
            else:
                # Mensagens de erro detalhadas do formulário são exibidas no template
                messages.error(request, 'Ocorreu um erro ao salvar as alterações. Verifique os campos.')
                # Continua para o render para exibir os formulários com erros

    context = {
        'user_form': user_form,
        'perfil_form': perfil_form,
        'is_admin': is_admin,
    }
    return render(request, 'app_LyfeSync/conta.html', context)