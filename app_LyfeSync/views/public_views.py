# app_LyfeSync/views/public_views.py
from django.shortcuts import render, redirect
from django.core.mail import EmailMessage
from django.conf import settings
from django.contrib import messages
from django.http import HttpResponseRedirect
from django.urls import reverse
# -------------------------------------------------------------------
# VIEWS PÚBLICAS (Sem necessidade de login)
# -------------------------------------------------------------------

def home(request):
    """Página inicial do site."""
    # CORREÇÃO DE CAMINHO: Template movido para a subpasta 'public'
    return render(request, 'app_LyfeSync/public/home.html')

def sobre_nos(request):
    """Página sobre a equipe e missão."""
    # CORREÇÃO DE CAMINHO: Template movido para a subpasta 'public'
    return render(request, 'app_LyfeSync/public/sobreNos.html')

def contatos(request):
    """Processa e renderiza a página de contato com envio de e-mail."""
    if request.method == 'POST':
        # 1. Captura os dados do formulário
        email_remetente = request.POST.get('email')
        assunto = request.POST.get('assunto')
        mensagem = request.POST.get('mensagem')
        anexo = request.FILES.get('anexo')
        
        # 2. Define o destinatário e o corpo do e-mail
        destinatario = ['fedcvn@gmail.com']
        
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
            # O anexo.read() já deve ser binário e o content_type é lido do arquivo
            mail.attach(anexo.name, anexo.read(), anexo.content_type)
        
        # 5. Tenta enviar o e-mail
        try:
            mail.send(fail_silently=False)
            messages.success(request, 'Mensagem enviada com sucesso! Em 48h entraremos em contato.')
            # Redireciona para a mesma página para limpar o POST
            return HttpResponseRedirect(reverse('contatos')) 
        except Exception as e:
            print(f"ERRO AO ENVIAR EMAIL: {e}")
            messages.error(request, f'Ocorreu um erro ao enviar a mensagem. Por favor, tente novamente mais tarde.')

    return render(request, 'app_LyfeSync/public/contatos.html')