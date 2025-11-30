from django.shortcuts import render
from django.contrib import messages
from django.http import HttpResponseRedirect
from django.urls import reverse
import yagmail
import tempfile
from decouple import config

# -------------------------------------------------------------------
# VIEWS PÚBLICAS (Sem necessidade de login)
# -------------------------------------------------------------------

def home(request):
    return render(request, 'app_LyfeSync/public/home.html')

def sobre_nos(request):
    return render(request, 'app_LyfeSync/public/sobreNos.html')

def contatos(request):
    if request.method == 'POST':
        # 1. Captura os dados do formulário
        email_remetente = request.POST.get('email')
        assunto = request.POST.get('assunto')
        mensagem = request.POST.get('mensagem')
        anexo = request.FILES.get('anexo')

        # 2. Destinatário do e-mail
        destinatario = ['fedcvn@gmail.com']  # coloque aqui o e-mail que vai receber os contatos

        # 3. Corpo do e-mail
        corpo_email = (
            f"Mensagem de Contato do Site LyfeSync:\n\n"
            f"E-mail (Identificador): {email_remetente}\n"
            f"Assunto: {assunto}\n\n"
            f"Mensagem:\n"
            f"----------------------------------------\n"
            f"{mensagem}\n"
            f"----------------------------------------"
        )

        try:
            # 4. Cria cliente yagmail
            yag = yagmail.SMTP(user=config('EMAIL_HOST_USER'), password=config('EMAIL_HOST_PASSWORD'))

            # 5. Envia e-mail
            if anexo:
            # cria arquivo temporário no disco
                with tempfile.NamedTemporaryFile(delete=False, suffix=anexo.name) as temp:
                    for chunk in anexo.chunks():
                        temp.write(chunk)
                        temp_path = temp.name

                        yag.send(
                            to=destinatario,
                            subject=f"[CONTATO LYFESYNC] {assunto}",
                            contents=corpo_email,
                            attachments=[temp_path]
                        )
                    else:
                        yag.send(
                            to=destinatario,
                            subject=f"[CONTATO LYFESYNC] {assunto}",
                            contents=corpo_email
                        )
            # 6. Feedback de sucesso
            messages.success(request, 'Mensagem enviada com sucesso! Em 48h entraremos em contato.')
            return HttpResponseRedirect(reverse('contatos'))

        except Exception as e:
            # 7. Feedback de erro
            print(f"ERRO AO ENVIAR EMAIL: {e}")
            messages.error(request, 'Ocorreu um erro ao enviar a mensagem. Por favor, tente novamente mais tarde.')

    return render(request, 'app_LyfeSync/public/contatos.html')