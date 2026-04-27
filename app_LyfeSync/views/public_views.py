from django.shortcuts import render
from django.contrib import messages
from django.http import HttpResponseRedirect
from django.urls import reverse
import os
import tempfile

import yagmail
from decouple import config

MAX_UPLOAD_SIZE = 5 * 1024 * 1024  # 5MB


# -------------------------------------------------------------------
# VIEWS PUBLICAS (Sem necessidade de login)
# -------------------------------------------------------------------


def home(request):
    return render(request, "app_LyfeSync/public/home.html")


def sobre_nos(request):
    return render(request, "app_LyfeSync/public/sobreNos.html")


def contatos(request):
    if request.method == "POST":
        # 1. Captura os dados do formulario
        email_remetente = request.POST.get("email")
        assunto = request.POST.get("assunto")
        mensagem = request.POST.get("mensagem")
        anexo = request.FILES.get("anexo")

        if anexo and anexo.size > MAX_UPLOAD_SIZE:
            messages.error(request, "O anexo excede o limite de 5MB.")
            return HttpResponseRedirect(reverse("contatos"))

        # 2. Destinatario do e-mail
        destinatario = ["fedcvn@gmail.com"]  # e-mail que recebe os contatos

        # 3. Corpo do e-mail
        corpo_email = (
            "Mensagem de Contato do Site LyfeSync:\n\n"
            f"E-mail (Identificador): {email_remetente}\n"
            f"Assunto: {assunto}\n\n"
            "Mensagem:\n"
            "----------------------------------------\n"
            f"{mensagem}\n"
            "----------------------------------------"
        )

        try:
            email_user = config("EMAIL_HOST_USER", default=None)
            email_password = config("EMAIL_HOST_PASSWORD", default=None)
            if not email_user or not email_password:
                raise ValueError("Credenciais de e-mail não configuradas no ambiente.")

            # 4. Cria cliente yagmail
            yag = yagmail.SMTP(
                user=email_user,
                password=email_password,
            )

            # 5. Envia e-mail
            if anexo:
                # Salva o anexo temporariamente para envio
                temp_path = None
                with tempfile.NamedTemporaryFile(delete=False, suffix=anexo.name) as temp:
                    for chunk in anexo.chunks():
                        temp.write(chunk)
                    temp_path = temp.name

                try:
                    yag.send(
                        to=destinatario,
                        subject=f"[CONTATO LYFESYNC] {assunto}",
                        contents=corpo_email,
                        attachments=[temp_path],
                    )
                finally:
                    if temp_path and os.path.exists(temp_path):
                        os.remove(temp_path)
            else:
                yag.send(
                    to=destinatario,
                    subject=f"[CONTATO LYFESYNC] {assunto}",
                    contents=corpo_email,
                )

            # 6. Feedback de sucesso
            messages.success(
                request, "Mensagem enviada com sucesso! Em 48h entraremos em contato."
            )
            return HttpResponseRedirect(reverse("contatos"))

        except Exception as e:
            # 7. Feedback de erro
            print(f"ERRO AO ENVIAR EMAIL: {e}")
            messages.error(
                request,
                "Ocorreu um erro ao enviar a mensagem. Por favor, tente novamente mais tarde.",
            )

    return render(request, "app_LyfeSync/public/contatos.html")
