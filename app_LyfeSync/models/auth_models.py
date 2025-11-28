#models/auth_models
from django.db import models
from django.contrib.auth import get_user_model
from django.db.models.signals import post_save
from django.dispatch import receiver

# Obtém o modelo de usuário ativo do Django (necessário para a FK em PerfilUsuario)
User = get_user_model()

# ===================================================================
# MODELOS EXTERNOS (MANAGED=FALSE) - Referenciando tabelas existentes
# ===================================================================

class AuthUser(models.Model):
    # Tabela AuthUser (Django default)
    password = models.CharField(max_length=128)
    last_login = models.DateTimeField(blank=True, null=True)
    is_superuser = models.IntegerField()
    username = models.CharField(unique=True, max_length=150)
    first_name = models.CharField(max_length=150)
    last_name = models.CharField(max_length=150)
    email = models.CharField(max_length=254)
    is_staff = models.IntegerField()
    is_active = models.IntegerField()
    date_joined = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'auth_user'
        verbose_name = "Usuário do Sistema (Auth)"
        verbose_name_plural = "Usuários do Sistema (Auth)"

class AccountEmailaddress(models.Model):
    # Tabela AccountEmailaddress (django-allauth)
    email = models.CharField(max_length=254)
    verified = models.IntegerField()
    primary = models.IntegerField()
    # FK para AuthUser
    user = models.ForeignKey(AuthUser, models.DO_NOTHING) 

    class Meta:
        managed = False
        db_table = 'account_emailaddress'
        unique_together = (('user', 'email'),)

class AuthGroup(models.Model):
    name = models.CharField(unique=True, max_length=150)

    class Meta:
        managed = False
        db_table = 'auth_group'

class AuthGroupPermissions(models.Model):
    id = models.BigAutoField(primary_key=True)
    group = models.ForeignKey(AuthGroup, models.DO_NOTHING)
    permission = models.ForeignKey('AuthPermission', models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'auth_group_permissions'
        unique_together = (('group', 'permission'),)

class AuthPermission(models.Model):
    name = models.CharField(max_length=255)
    content_type = models.ForeignKey('DjangoContentType', models.DO_NOTHING)
    codename = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = 'auth_permission'
        unique_together = (('content_type', 'codename'),)

class AuthUserGroups(models.Model):
    id = models.BigAutoField(primary_key=True)
    user = models.ForeignKey(AuthUser, models.DO_NOTHING)
    group = models.ForeignKey(AuthGroup, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'auth_user_groups'
        unique_together = (('user', 'group'),)

class AuthUserUserPermissions(models.Model):
    id = models.BigAutoField(primary_key=True)
    user = models.ForeignKey(AuthUser, models.DO_NOTHING)
    permission = models.ForeignKey(AuthPermission, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'auth_user_user_permissions'
        unique_together = (('user', 'permission'),)

class DjangoAdminLog(models.Model):
    action_time = models.DateTimeField()
    object_id = models.TextField(blank=True, null=True)
    object_repr = models.CharField(max_length=200)
    action_flag = models.PositiveSmallIntegerField()
    change_message = models.TextField()
    content_type = models.ForeignKey('DjangoContentType', models.DO_NOTHING, blank=True, null=True)
    user = models.ForeignKey(AuthUser, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'django_admin_log'

class DjangoContentType(models.Model):
    app_label = models.CharField(max_length=100)
    model = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = 'django_content_type'
        unique_together = (('app_label', 'model'),)

class DjangoMigrations(models.Model):
    id = models.BigAutoField(primary_key=True)
    app = models.CharField(max_length=255)
    name = models.CharField(max_length=255)
    applied = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'django_migrations'

class DjangoSession(models.Model):
    session_key = models.CharField(primary_key=True, max_length=40)
    session_data = models.TextField()
    expire_date = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'django_session'

class DjangoSite(models.Model):
    domain = models.CharField(unique=True, max_length=100)
    name = models.CharField(max_length=50)

    class Meta:
        managed = False
        db_table = 'django_site'

class SocialaccountSocialaccount(models.Model):
    # Tabela SocialaccountSocialaccount (django-allauth)
    provider = models.CharField(max_length=200)
    uid = models.CharField(max_length=191)
    last_login = models.DateTimeField()
    date_joined = models.DateTimeField()
    extra_data = models.JSONField()
    user = models.ForeignKey(AuthUser, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'socialaccount_socialaccount'
        unique_together = (('provider', 'uid'),)

class SocialaccountSocialapp(models.Model):
    provider = models.CharField(max_length=30)
    name = models.CharField(max_length=40)
    client_id = models.CharField(max_length=191)
    secret = models.CharField(max_length=191)
    key = models.CharField(max_length=191)
    provider_id = models.CharField(max_length=200)
    settings = models.JSONField()

    class Meta:
        managed = False
        db_table = 'socialaccount_socialapp'

class SocialaccountSocialappSites(models.Model):
    id = models.BigAutoField(primary_key=True)
    socialapp = models.ForeignKey(SocialaccountSocialapp, models.DO_NOTHING)
    site = models.ForeignKey(DjangoSite, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'socialaccount_socialapp_sites'
        unique_together = (('socialapp', 'site'),)

class SocialaccountSocialtoken(models.Model):
    token = models.TextField()
    token_secret = models.TextField()
    expires_at = models.DateTimeField(blank=True, null=True)
    account = models.ForeignKey(SocialaccountSocialaccount, models.DO_NOTHING)
    app = models.ForeignKey(SocialaccountSocialapp, models.DO_NOTHING, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'socialaccount_socialtoken'
        unique_together = (('app', 'account'),)


# ===================================================================
# MODELO DE PERFIL ESTENDIDO (MANAGED=TRUE)
# ===================================================================

TIPO_USUARIO_CHOICES = [
    ('Cliente', 'Cliente'),
    ('Administrador', 'Administrador'),
]

class PerfilUsuario(models.Model):
    """
    Modelo de Perfil Estendido para o Usuário Padrão do Django.
    Adiciona a coluna 'tipoUsuario'.
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='perfil')
    
    # Nova coluna para o banco de dados (BD MySQL)
    tipoUsuario = models.CharField(
        max_length=15,
        choices=TIPO_USUARIO_CHOICES,
        default='Cliente',
        verbose_name="Tipo de Usuário"
    )

    def __str__(self):
        return f'Perfil de {self.user.username}'

# --- Sinais para criar e salvar o perfil automaticamente ---

@receiver(post_save, sender=User)
def criar_ou_atualizar_perfil_usuario(sender, instance, created, **kwargs):
    """
    Garante que um PerfilUsuario é criado automaticamente quando um novo User é criado.
    """
    if created:
        PerfilUsuario.objects.create(user=instance)
    # Se o perfil já existe, apenas salva, garantindo a sincronia.
    try:
        instance.perfil.save()
    except PerfilUsuario.DoesNotExist:
        pass


@receiver(post_save, sender=User)
def sincronizar_admin_status(sender, instance, **kwargs):
    """
    Sincroniza automaticamente o tipoUsuario com o status de superusuário do Django.
    """
    if hasattr(instance, 'perfil'):
        is_admin_flag = instance.is_superuser or instance.is_staff
        tipo_atual = instance.perfil.tipoUsuario
        
        # Se for um superuser/staff e não estiver como Administrador no perfil
        if is_admin_flag and tipo_atual != 'Administrador':
            instance.perfil.tipoUsuario = 'Administrador'
            instance.perfil.save()
        # Se NÃO for superuser/staff, mas estiver como Administrador no perfil
        elif not is_admin_flag and tipo_atual == 'Administrador':
            # Rebaixa para Cliente
            instance.perfil.tipoUsuario = 'Cliente'
            instance.perfil.save()