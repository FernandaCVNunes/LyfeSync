#models/selfcare_models.py
from django.db import models
from django.conf import settings
from django.contrib.auth import get_user_model
from django.utils import timezone

# Obtém o modelo de usuário ativo (geralmente User)
User = get_user_model()

# ===================================================================
# 1. HÁBITOS
# ===================================================================
class Habito(models.Model):
    """Modelo para registro dos hábitos que o usuário deseja acompanhar."""
    # 1. Definição das constantes
    DIARIO = 'DIARIO'
    SEMANAL = 'SEMANAL'
    MENSAL = 'MENSAL'
    PERSONALIZADO = 'PERSONALIZADO'
    
    # 2. Definição da lista de CHOICES
    FREQUENCIA_CHOICES = [
        (DIARIO, 'Diário'),
        (SEMANAL, 'Semanal'),
        (MENSAL, 'Mensal'),
        (PERSONALIZADO, 'Personalizado'),
    ]
    
    # 3. Definição dos campos
    id = models.BigAutoField(primary_key=True) 
    idusuario = models.ForeignKey(User, on_delete=models.CASCADE) # Assumindo um FK para o usuário
    nome = models.CharField(max_length=200, verbose_name="Nome do Hábito")
    data_inicio = models.DateField(verbose_name="Data de Início")
    data_fim = models.DateField(verbose_name="Data de Fim", null=True, blank=True)
    quantidade = models.IntegerField(verbose_name="Quantidade/Meta")
    
    # 4. Campo 'frequencia' usando as CHOICES
    frequencia = models.CharField(
        max_length=20, 
        choices=FREQUENCIA_CHOICES, 
        default=DIARIO, 
        verbose_name="Frequência"
    )
    
    alvo = models.CharField(max_length=255, verbose_name="Alvo/Objetivo", null=True, blank=True)
    descricao = models.TextField(verbose_name="Descrição Detalhada", null=True, blank=True)
    
    # Chave estrangeira para o modelo de usuário do Django
    usuario = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        verbose_name="Usuário", 
        related_name="habitos"
    ) 

    def __str__(self):
        return self.nome
        
    class Meta:
        db_table = 'app_lyfesync_habito' 
        verbose_name = "Hábito"
        verbose_name_plural = "Hábitos"


# ===================================================================
# 2. STATUS DIÁRIO (Acompanhamento dos Hábitos)
# ===================================================================
class StatusDiario(models.Model):
    """Registro diário do status de conclusão de um hábito."""
    id = models.BigAutoField(primary_key=True)
    data = models.DateField(verbose_name="Data do Registro")
    # O campo BooleanField mapeia para INTEGER (0 ou 1) no banco de dados.
    concluido = models.BooleanField(verbose_name="Concluído") 
    
    # Chave Estrangeira para o modelo Habito
    habito = models.ForeignKey(
        Habito, 
        on_delete=models.CASCADE, 
        verbose_name="Hábito Relacionado",
        related_name="status_diarios"
    ) 

    def __str__(self):
        status = "Concluído" if self.concluido else "Pendente"
        return f"{self.habito.nome} em {self.data}: {status}"
        
    class Meta:
        db_table = 'app_lyfesync_statusdiario' 
        # Garante que um hábito só pode ter um status por dia
        unique_together = (('habito', 'data'),)
        verbose_name = "Status Diário"
        verbose_name_plural = "Status Diários"


# ===================================================================
# 3. AFIRMAÇÕES
# ===================================================================
class Afirmacao(models.Model):
    """Modelo para as afirmações diárias do usuário."""
    idafirmacao = models.AutoField(db_column='idAfirmacao', primary_key=True)
    data = models.DateField(blank=True, null=True, verbose_name="Data da Afirmação")
    nomeafirmacao = models.CharField(db_column='nomeAfirmacao', max_length=100, blank=True, null=True, verbose_name="Título")
    descricaoafirmacao = models.TextField(db_column='descricaoAfirmacao', blank=True, null=True, verbose_name="Conteúdo")
    
    # Chave Estrangeira para o modelo de usuário
    idusuario = models.ForeignKey(
        User, 
        models.CASCADE, 
        db_column='idUsuario', 
        blank=True, 
        null=True, 
        verbose_name="Usuário"
    ) 

    def __str__(self):
        return self.nomeafirmacao or f"Afirmação {self.idafirmacao}"

    class Meta:
        db_table = 'afirmacao'
        verbose_name = "Afirmação"
        verbose_name_plural = "Afirmações"


# ===================================================================
# 4. GRATIDÃO
# ===================================================================
class Gratidao(models.Model):
    """Modelo para registro diário de gratidões."""
    idgratidao = models.AutoField(db_column='idGratidao', primary_key=True)
    data = models.DateField(blank=True, null=True, verbose_name="Data da Gratidão")
    nomegratidao = models.CharField(db_column='nomeGratidao', max_length=100, blank=True, null=True, verbose_name="Título")
    descricaogratidao = models.TextField(db_column='descricaoGratidao', blank=True, null=True, verbose_name="Descrição")
    
    # Chave Estrangeira para o modelo de usuário
    idusuario = models.ForeignKey(
        User, 
        models.CASCADE, 
        db_column='idUsuario', 
        blank=True, 
        null=True, 
        verbose_name="Usuário"
    ) 

    def __str__(self):
        return self.nomegratidao or f"Gratidão {self.idgratidao}"

    class Meta:
        db_table = 'gratidao'
        verbose_name = "Gratidão"
        verbose_name_plural = "Gratidões"

# ===================================================================
# 5A. TIPOS DE HUMOR (Tabela de Classificação - COM icone)
# ===================================================================
class HumorTipo(models.Model):
    """Representa os diferentes tipos de humor (e.g., Feliz, Triste, Ansioso)."""
    id_tipo_humor = models.AutoField(db_column='idTipoHumor', primary_key=True)
    
    estado = models.CharField(
        max_length=50, 
        verbose_name='Nome do Estado de Humor', 
        unique=True
    )
    
    # CORREÇÃO: Tornando o campo 'icone' opcional para a migração e flexibilidade.
    icone = models.CharField(
        max_length=50, 
        verbose_name='Ícone', 
        blank=True, # Opcional no formulário (Admin)
        null=True   # Opcional no banco de dados
    )
    
    descricao = models.TextField(
        max_length=255, 
        verbose_name='Descrição Breve', 
        blank=True,
        null=True
    )

    class Meta:
        db_table = 'humor_tipo'
        verbose_name = 'Tipo de Humor'
        verbose_name_plural = 'Tipos de Humor'
        ordering = ['estado']

    def __str__(self):
        return self.estado

# ===================================================================
# 5B. REGISTRO DE HUMOR DIÁRIO (Atualizado com FK para HumorTipo)
# ===================================================================
class Humor(models.Model):
    """Registro diário do estado de humor de um usuário."""
    idhumor = models.AutoField(db_column='idHumor', primary_key=True)
    
    idusuario = models.ForeignKey(
        User, 
        models.CASCADE, 
        db_column='idUsuario',
        verbose_name='Usuário',
        related_name='registros_humor'
    )
    
    data = models.DateField(
        verbose_name='Data do Registro', 
        help_text='A data em que o humor foi registrado.'
    )
    
    # AGORA USA FK para o novo modelo HumorTipo
    estado = models.ForeignKey(
        HumorTipo,
        on_delete=models.PROTECT, # Protege o tipo de humor de ser apagado se houver registros
        verbose_name='Estado de Humor',
        related_name='registros_diarios',
        null=True,  # Permite que o campo seja NULL no banco de dados
        blank=True  # Permite que o campo seja opcional no formulário
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
        # Garante que o usuário só pode registrar 1 humor por dia
        unique_together = ('idusuario', 'data',) 

    def __str__(self):
        user_info = self.idusuario.username if self.idusuario else "Usuário Desconhecido"
        # Acessa o nome do estado pelo FK
        return f"{user_info} - {self.data} - {self.estado.estado}"


# ===================================================================
# 6. DICAS (Atualizado com FK para HumorTipo e managed=False removido)
# ===================================================================
class Dicas(models.Model):
    """Dicas relacionadas a diferentes estados de humor."""
    # CHAVE PRIMÁRIA
    idDica = models.AutoField(
        primary_key=True,
        verbose_name="ID da Dica"
    )

    # AGORA USA FK para o novo modelo HumorTipo
    humor_relacionado = models.ForeignKey(
        HumorTipo,
        on_delete=models.PROTECT, # Recomendado para não apagar dicas acidentalmente
        verbose_name="Humor Relacionado",
        related_name='dicas' # Permite acessar todas as dicas de um humor via HumorTipo.dicas.all()
    )
    
    nomeDica = models.CharField(
        max_length=200,
        verbose_name="Nome da Dica"
    )
    
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
        # managed = False FOI REMOVIDO para que o Django crie e gerencie a tabela
        db_table = 'dicas'
        verbose_name = "Dica de Humor"
        verbose_name_plural = "Dicas de Humor"
        
    def __str__(self):
        # Acessa o nome do estado pelo FK
        return f"Dica para {self.humor_relacionado.estado}: {self.nomeDica}"


# ===================================================================
# 7. RELATÓRIOS
# ===================================================================
class Relatorio(models.Model):
    """Modelo para armazenar metadados de relatórios gerados."""
    idrelatorio = models.AutoField(db_column='idRelatorio', primary_key=True)
    tiporelatorio = models.CharField(db_column='tipoRelatorio', max_length=50, blank=True, null=True, verbose_name="Tipo de Relatório")
    dados = models.TextField(blank=True, null=True, help_text="Dados brutos ou serializados do relatório")
    caminhoarquivo = models.TextField(db_column='caminhoArquivo', blank=True, null=True, verbose_name="Caminho do Arquivo (URL/Path)")
    
    # Chave Estrangeira para o modelo de usuário
    idusuario = models.ForeignKey(
        User, 
        models.CASCADE, 
        db_column='idUsuario', 
        blank=True, 
        null=True,
        verbose_name="Usuário"
    )

    def __str__(self):
        return f"Relatório de {self.tiporelatorio or 'Tipo Desconhecido'} ({self.idrelatorio})"

    class Meta:
        db_table = 'relatorio'
        verbose_name = "Relatório"
        verbose_name_plural = "Relatórios"