from django.db import models
from django.conf import settings

class ActivityLog(models.Model):
    """
    Rastreia atividades importantes do usuário e do sistema para auditoria e segurança.
    """
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='activity_logs',
        verbose_name='Usuário'
    )
    action = models.CharField(
        max_length=255,
        verbose_name='Ação Realizada'
    )
    timestamp = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Carimbo de Data/Hora'
    )
    ip_address = models.GenericIPAddressField(
        null=True,
        blank=True,
        verbose_name='Endereço IP'
    )
    details = models.JSONField(
        null=True,
        blank=True,
        help_text='Detalhes adicionais da ação em formato JSON.'
    )

    class Meta:
        verbose_name = 'Registro de Atividade'
        verbose_name_plural = 'Registros de Atividades'
        ordering = ['-timestamp']

    def __str__(self):
        return f'{self.timestamp.strftime("%Y-%m-%d %H:%M")} - {self.action}'


class SystemConfiguration(models.Model):
    """
    Armazena configurações globais do sistema, como limites, chaves de API, etc.
    """
    key = models.CharField(
        max_length=100,
        unique=True,
        verbose_name='Chave de Configuração'
    )
    value = models.TextField(
        verbose_name='Valor da Configuração'
    )
    data_type = models.CharField(
        max_length=20,
        choices=[
            ('str', 'String'),
            ('int', 'Integer'),
            ('bool', 'Boolean'),
            ('json', 'JSON')
        ],
        default='str',
        verbose_name='Tipo de Dado'
    )
    description = models.TextField(
        blank=True,
        verbose_name='Descrição'
    )
    last_updated = models.DateTimeField(
        auto_now=True,
        verbose_name='Última Atualização'
    )

    class Meta:
        verbose_name = 'Configuração do Sistema'
        verbose_name_plural = 'Configurações do Sistema'

    def __str__(self):
        return f'{self.key}: {self.value[:50]}...'