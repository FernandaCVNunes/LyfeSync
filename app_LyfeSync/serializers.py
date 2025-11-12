#app_LyfeSync/serializer.py
import uuid
from django.db import models
from django.conf import settings

# Acessa o modelo de Usuário padrão do Django
AuthUser = settings.AUTH_USER_MODEL

class UserNotificationSettings(models.Model):
    """
    Armazena as preferências de notificação do usuário.
    Relaciona-se 1:1 com o modelo de usuário principal.
    """
    user = models.OneToOneField(
        AuthUser,
        on_delete=models.CASCADE,
        related_name='notification_settings',
        verbose_name="Usuário"
    )
    email_notifications = models.BooleanField(
        default=True,
        verbose_name="Notificações por E-mail",
        help_text="Receber atualizações semanais e alertas por e-mail."
    )
    in_app_reminders = models.BooleanField(
        default=True,
        verbose_name="Lembretes no Aplicativo",
        help_text="Receber lembretes de hábitos e tarefas."
    )
    last_updated = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Configuração de Notificação do Usuário"
        verbose_name_plural = "Configurações de Notificação do Usuário"

    def __str__(self):
        return f"Configurações de Notificação para {self.user.username}"

class DeviceToken(models.Model):
    """
    Armazena tokens de dispositivo (ex: FCM/APNS) para envio de notificações push.
    """
    user = models.models.ForeignKey(
        AuthUser,
        on_delete=models.CASCADE,
        related_name='device_tokens',
        verbose_name="Usuário"
    )
    token = models.CharField(
        max_length=255,
        unique=True,
        verbose_name="Token do Dispositivo"
    )
    device_type = models.CharField(
        max_length=50,
        choices=[('ios', 'iOS'), ('android', 'Android'), ('web', 'Web')],
        default='web',
        verbose_name="Tipo de Dispositivo"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Token de Dispositivo"
        verbose_name_plural = "Tokens de Dispositivo"
        unique_together = ('user', 'device_type', 'token')

    def __str__(self):
        return f"Token de {self.device_type} para {self.user.username}"

