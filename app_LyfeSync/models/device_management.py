from django.db import models
from django.conf import settings

class DeviceToken(models.Model):
    """
    Armazena tokens de dispositivo (como tokens FCM) para enviar
    notificações push.
    """
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='device_tokens',
        verbose_name='Usuário'
    )
    token = models.CharField(
        max_length=255,
        unique=True,
        verbose_name='Token de Dispositivo'
    )
    device_type = models.CharField(
        max_length=10,
        choices=[('ios', 'iOS'), ('android', 'Android'), ('web', 'Web')],
        default='web',
        verbose_name='Tipo de Dispositivo'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Criado em'
    )
    last_used = models.DateTimeField(
        auto_now=True,
        verbose_name='Última Utilização'
    )

    class Meta:
        verbose_name = 'Token de Dispositivo'
        verbose_name_plural = 'Tokens de Dispositivo'
        # Garante que um usuário não tenha o mesmo token duplicado,
        # embora o campo 'token' já seja unique=True.
        unique_together = ('user', 'token')

    def __str__(self):
        return f'{self.device_type} token para {self.user.username}'