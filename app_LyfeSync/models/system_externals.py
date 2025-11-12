# system_externals.py
# Define modelos para armazenar configurações de integração com sistemas externos.

from django.db import models
from django.conf import settings # Para referenciar o modelo de Usuário personalizado

class ExternalIntegrationSetting(models.Model):
    """
    Configurações para APIs ou serviços externos (ex: Clima, Calendário, etc.).
    """
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='external_settings',
        verbose_name='Usuário'
    )
    api_name = models.CharField(
        max_length=100,
        unique=True,
        verbose_name='Nome da API/Serviço'
    )
    api_key_encrypted = models.TextField(
        verbose_name='Chave de API (Criptografada)',
        help_text='Armazene chaves e tokens de forma segura e criptografada.'
    )
    is_active = models.BooleanField(
        default=False,
        verbose_name='Ativo'
    )
    last_synced = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='Última Sincronização'
    )

    class Meta:
        verbose_name = 'Configuração de Integração Externa'
        verbose_name_plural = 'Configurações de Integrações Externas'

    def __str__(self):
        return f'{self.api_name} - {self.user.username}'

# Nota: A lógica de criptografia e descriptografia deve ser implementada em Services/Managers,
# e não diretamente no modelo.