from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.db.models.signals import post_save
from django.dispatch import receiver


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
    # FK para AuthUser com models.DO_NOTHING, pois é managed=False
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
        
class Usuario(models.Model):
    idusuario = models.AutoField(db_column='idUsuario', primary_key=True) 
    nome = models.CharField(max_length=100, blank=True, null=True)
    datanascimento = models.DateField(db_column='dataNascimento', blank=True, null=True)
    email = models.CharField(unique=True, max_length=100, blank=True, null=True)
    senha = models.CharField(max_length=100, blank=True, null=True)
    
    def __str__(self):
        return self.nome or self.email or f"Usuário Legado {self.idusuario}"

    class Meta:
        managed = False
        db_table = 'usuario'

TIPO_USUARIO_CHOICES = [
    ('Cliente', 'Cliente'),
    ('Administrador', 'Administrador'),
]

class PerfilUsuario(models.Model):
    """
    Modelo de Perfil Estendido para o Usuário Padrão do Django.
    Adiciona a coluna 'tipoUsuario' ao banco de dados MySQL.
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
    # Usamos try/except para evitar erros em migrações
    try:
        instance.perfil.save()
    except PerfilUsuario.DoesNotExist:
        pass


@receiver(post_save, sender=User)
def sincronizar_admin_status(sender, instance, **kwargs):
    """
    Sincroniza automaticamente o tipoUsuario com o status de superusuário do Django.
    Isso é vital para evitar inconsistências.
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


# ===================================================================
# MODELOS DA APLICAÇÃO app_LyfeSync (Managed = True)
# ===================================================================

# -------------------------------------------------------------------
# 1. HÁBITOS
# -------------------------------------------------------------------
class Habito(models.Model):
    id = models.BigAutoField(primary_key=True) 
    
    nome = models.CharField(max_length=200)
    data_inicio = models.DateField(default=timezone.now)
    data_fim = models.DateField(blank=True, null=True)
    
    quantidade = models.IntegerField(default=1) 
    
    frequencia = models.CharField(max_length=10) # Ex: Diário, Semanal
    alvo = models.CharField(max_length=200, blank=True)
    descricao = models.TextField(blank=True)
    
    # FK para o modelo de usuário do Django com CASCADE
    usuario = models.ForeignKey(User, on_delete=models.CASCADE) 

    def __str__(self):
        return self.nome
        
    class Meta:
        db_table = 'app_lyfesync_habito' 
        verbose_name = "Hábito"
        verbose_name_plural = "Hábitos"


# -------------------------------------------------------------------
# 2. STATUS DIÁRIO
# -------------------------------------------------------------------
class StatusDiario(models.Model):
    id = models.BigAutoField(primary_key=True)
    data = models.DateField()
    # Assume que o campo no DB é INTEGER (0 ou 1) e mapeia para Boolean
    concluido = models.BooleanField() 
    
    # FK para o modelo Habito com CASCADE
    habito = models.ForeignKey(Habito, on_delete=models.CASCADE) 

    def __str__(self):
        status = "Concluído" if self.concluido else "Pendente"
        return f"{self.habito.nome} em {self.data}: {status}"
        
    class Meta:
        db_table = 'app_lyfesync_statusdiario' 
        unique_together = (('habito', 'data'),)
        verbose_name = "Status Diário"
        verbose_name_plural = "Status Diários"


# -------------------------------------------------------------------
# 3. AFIRMAÇÕES
# -------------------------------------------------------------------
class Afirmacao(models.Model):
    idafirmacao = models.AutoField(db_column='idAfirmacao', primary_key=True)
    data = models.DateField(blank=True, null=True)
    nomeafirmacao = models.CharField(db_column='nomeAfirmacao', max_length=100, blank=True, null=True)
    descricaoafirmacao = models.TextField(db_column='descricaoAfirmacao', blank=True, null=True)
    
    # FK corrigida para User (get_user_model()) com CASCADE
    idusuario = models.ForeignKey(User, models.CASCADE, db_column='idUsuario', blank=True, null=True) 

    def __str__(self):
        return self.nomeafirmacao or f"Afirmação {self.idafirmacao}"

    class Meta:
        db_table = 'afirmacao'
        verbose_name = "Afirmação"
        verbose_name_plural = "Afirmações"


# -------------------------------------------------------------------
# 4. GRATIDÃO
# -------------------------------------------------------------------
class Gratidao(models.Model):
    idgratidao = models.AutoField(db_column='idGratidao', primary_key=True)
    data = models.DateField(blank=True, null=True)
    nomegratidao = models.CharField(db_column='nomeGratidao', max_length=100, blank=True, null=True)
    descricaogratidao = models.TextField(db_column='descricaoGratidao', blank=True, null=True)
    
    # FK que aponta para o usuário do Django (auth_user.id)
    idusuario = models.ForeignKey(User, models.CASCADE, db_column='idUsuario', blank=True, null=True) 

    def __str__(self):
        return self.nomegratidao or f"Gratidão {self.idgratidao}"

    class Meta:
        db_table = 'gratidao'
        verbose_name = "Gratidão"
        verbose_name_plural = "Gratidões"


# -------------------------------------------------------------------
# 5. HUMOR
# -------------------------------------------------------------------
class Humor(models.Model):
    idhumor = models.AutoField(db_column='idHumor', primary_key=True)
    
    idusuario = models.ForeignKey(
        User, 
        models.CASCADE, 
        db_column='idUsuario',
        verbose_name='Usuário'
    )
    
    ESTADOS_HUMOR = [
        ('Feliz', '😀 Feliz'),
        ('Calmo', '😌 Calmo'),
        ('Ansioso', '😟 Ansioso'),
        ('Triste', '😥 Triste'),
        ('Irritado', '😡 Irritado'),
    ]
    
    data = models.DateField(
        verbose_name='Data do Registro', 
        help_text='A data em que o humor foi registrado.'
    )
    
    estado = models.CharField(
        max_length=10, # Alterei para 10, o suficiente para os choices acima (o seu estava 100)
        choices=ESTADOS_HUMOR,
        verbose_name='Estado de Humor'
    )
    
    descricaohumor = models.TextField(
        db_column='descricaoHumor', 
        max_length=500,
        blank=True,
        null=True,
        verbose_name='Descrição do Humor',
        help_text='Opcional: Descreva o que motivou este humor.'
    )
    
    data_registro = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Momento do Registro'
    )

    class Meta:
        db_table = 'humor'
        verbose_name = 'Registro de Humor'
        verbose_name_plural = 'Registros de Humor'
        ordering = ['-data']
        unique_together = ('idusuario', 'data',) 

    def __str__(self):
        user_info = self.idusuario.username if self.idusuario else "Usuário Desconhecido"
        return f"{user_info} - {self.data} - {self.estado}"

# -------------------------------------------------------------------
# 6. DICAS
# -------------------------------------------------------------------

HUMOR_CHOICES = [
    ('Feliz', 'Feliz'),
    ('Calmo', 'Calmo'),
    ('Ansioso', 'Ansioso'),
    ('Triste', 'Triste'),
    ('Irritado', 'Irritado'),
]

class Dicas(models.Model):
    # CHAVE PRIMÁRIA
    # Deve corresponder exatamente ao nome da coluna PK no banco: idDica
    idDica = models.AutoField(
        primary_key=True,
        verbose_name="ID da Dica"
    )

    # Corrigido: 'estado' para 'TipoHumor' para corresponder ao DB
    TipoHumor = models.CharField(
        max_length=50,
        choices=HUMOR_CHOICES,
        default='Feliz',
        verbose_name="Humor Relacionado"
    )
    
    # Corrigido: 'nome_dica' para 'nomeDica' para corresponder ao DB
    nomeDica = models.CharField(
        max_length=200,
        verbose_name="Nome da Dica"
    )
    
    # Corrigido: 'descricao' para 'descricaoDica' para corresponder ao DB
    descricaoDica = models.TextField(
        verbose_name="Descrição da Dica",
        help_text="O conteúdo completo da dica, podendo incluir listas ou parágrafos."
    )

    # Campo para rastrear quem criou (opcional, mas boa prática)
    criado_por = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Criado Por"
    )
    
    data_criacao = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Data de Criação"
    )

    class Meta:
        # Permanece False, pois a tabela já existe
        managed = False
        # Nome exato da tabela no banco
        db_table = 'dicas'
        verbose_name = "Dica de Humor"
        verbose_name_plural = "Dicas de Humor"
        
    def __str__(self):
        # Mudando self.estado para self.TipoHumor e self.nome_dica para self.nomeDica
        return f"Dica para {self.TipoHumor}: {self.nomeDica}"

# -------------------------------------------------------------------
# 7. RELATÓRIOS
# -------------------------------------------------------------------
class Relatorio(models.Model):
    idrelatorio = models.AutoField(db_column='idRelatorio', primary_key=True)
    tiporelatorio = models.CharField(db_column='tipoRelatorio', max_length=50, blank=True, null=True)
    dados = models.TextField(blank=True, null=True)
    caminhoarquivo = models.TextField(db_column='caminhoArquivo', blank=True, null=True)
    
    # FK corrigida para User (get_user_model()) com CASCADE
    idusuario = models.ForeignKey(User, models.CASCADE, db_column='idUsuario', blank=True, null=True)

    def __str__(self):
        return f"Relatório de {self.tiporelatorio or 'Tipo Desconhecido'} ({self.idrelatorio})"

    class Meta:
        db_table = 'relatorio'
        verbose_name = "Relatório"
        verbose_name_plural = "Relatórios"