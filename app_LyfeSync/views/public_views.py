# app_LyfeSync/views/public_views.py
from django.shortcuts import render, redirect
from django.core.mail import EmailMessage
from django.conf import settings
from django.contrib import messages
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.contrib.auth import logout, login 
from django.contrib.auth.forms import UserCreationForm as CadastroForm 


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
    """Função de view para o cadastro de novos usuários."""
    if request.method == 'POST':
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