# user_profile_and_signals.py
# Define o Perfil do Usuário, Configurações de Notificação e os Handlers de Signal
# para criação automática dos modelos relacionados.

from django.db import models
from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver

# --- Modelos ---

class UserProfile(models.Model):
    """
    Modelo de Perfil do Usuário, estendendo o modelo CustomUser (One-to-One).
    Contém configurações e dados específicos do perfil.
    """
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='profile',
        verbose_name='Usuário'
    )
    bio = models.TextField(
        max_length=500,
        blank=True,
        verbose_name='Biografia/Sobre Mim'
    )
    timezone = models.CharField(
        max_length=50,
        default='America/Sao_Paulo',
        verbose_name='Fuso Horário Preferido'
    )
    preferred_language = models.CharField(
        max_length=10,
        default='pt-br',
        verbose_name='Idioma Preferido'
    )
    profile_image_url = models.URLField(
        max_length=200,
        blank=True,
        verbose_name='URL da Imagem de Perfil'
    )
    # Mudança: Removendo primary_key=True de OneToOneField para usar o ID padrão do Django,
    # que é o comportamento recomendado, a menos que haja uma necessidade específica.

    class Meta:
        verbose_name = 'Perfil do Usuário'
        verbose_name_plural = 'Perfis dos Usuários'

    def __str__(self):
        return f'Perfil de {self.user.username}'


class UserNotificationSettings(models.Model):
    """
    Modelo ADICIONADO: Armazena as preferências de notificação do usuário.
    Ligado ao CustomUser via One-to-One.
    """
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='notification_settings',
        verbose_name='Usuário'
    )
    email_updates = models.BooleanField(
        default=True,
        verbose_name="Receber newsletters e atualizações por e-mail"
    )
    task_reminders = models.BooleanField(
        default=True,
        verbose_name="Lembretes de Tarefas"
    )
    habit_alerts = models.BooleanField(
        default=True,
        verbose_name="Alertas de Hábitos (para metas)"
    )
    
    class Meta:
        verbose_name = 'Configuração de Notificação'
        verbose_name_plural = 'Configurações de Notificações'

    def __str__(self):
        return f'Notificações de {self.user.username}'

# --- Signals (Sinais) ---

@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_or_update_user_related_models(sender, instance, created, **kwargs):
    """
    Cria ou atualiza o UserProfile e UserNotificationSettings
    sempre que o modelo de usuário é salvo.
    """
    if created:
        # Se o usuário é novo, cria os modelos relacionados
        UserProfile.objects.create(user=instance)
        UserNotificationSettings.objects.create(user=instance)
    else:
        # Se o usuário já existe, garante que os modelos relacionados sejam salvos (atualizados)
        # Usa .save() para garantir que qualquer alteração de um signal anterior seja persistida
        try:
            instance.profile.save()
        except UserProfile.DoesNotExist:
             UserProfile.objects.create(user=instance) # Cria se por algum motivo faltar

        try:
            instance.notification_settings.save()
        except UserNotificationSettings.DoesNotExist:
            UserNotificationSettings.objects.create(user=instance) # Cria se por algum motivo faltar

# NOTA: O signal 'save_user_profile' foi removido e consolidado acima.