# test_models.py

import pytest
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import date
# Importa o erro específico que o Django levanta em caso de falha de UNIQUE_TOGETHER
from django.db.utils import IntegrityError 

# --- AJUSTE ESTES IMPORTS PARA SEU PROJETO ---
from ..models.auth_models import PerfilUsuario, DeviceToken
from ..models.selfcare_models import Habito, StatusDiario, HumorTipo, Humor
from ..models.auth_models import TIPO_USUARIO_CHOICES

# Obtém o modelo de usuário do Django
User = get_user_model()

# ===================================================================
# FIXTURES (Dados de Teste Reutilizáveis)
# ===================================================================

# Esta fixture cria um usuário padrão para ser usado em vários testes
# O parâmetro 'db' garante que o banco de dados de teste esteja pronto
@pytest.fixture
@pytest.mark.django_db
def usuario_cliente():
    """Cria e retorna um usuário padrão (não superusuário)."""
    return User.objects.create_user(
        username='teste_cliente',
        email='cliente@teste.com',
        password='senha_segura'
    )

@pytest.fixture
@pytest.mark.django_db
def usuario_admin():
    """Cria e retorna um superusuário."""
    # is_superuser=True e is_staff=True para acionar o sinal de sincronização
    return User.objects.create_superuser(
        username='teste_admin',
        email='admin@teste.com',
        password='senha_segura'
    )

@pytest.fixture
@pytest.mark.django_db
def habito_exemplo(usuario_cliente):
    """Cria e retorna um objeto Habito para testes."""
    return Habito.objects.create(
        usuario=usuario_cliente,
        nome="Beber Água",
        data_inicio=date.today(),
        quantidade=8,
        frequencia=Habito.DIARIO,
        alvo="Beber 8 copos de água por dia"
    )

@pytest.fixture
@pytest.mark.django_db
def humor_tipo_feliz():
    """Cria e retorna um objeto HumorTipo 'Feliz'."""
    return HumorTipo.objects.create(
        estado="Feliz",
        icone="smile-fill"
    )

# ===================================================================
# TESTES PARA auth_models.PerfilUsuario (com Sinais)
# ===================================================================

@pytest.mark.django_db
def test_perfilusuario_criacao_automatica(usuario_cliente):
    """Verifica se um PerfilUsuario é criado automaticamente após a criação do User."""
    
    # O sinal 'post_save' deve ter sido acionado pelo fixture
    perfil = PerfilUsuario.objects.get(user=usuario_cliente)
    
    assert perfil is not None
    assert perfil.tipoUsuario == 'Cliente'
    assert str(perfil) == f'Perfil de {usuario_cliente.username}'

@pytest.mark.django_db
def test_perfilusuario_sincronizacao_admin(usuario_cliente):
    """Verifica se o tipoUsuario muda para 'Administrador' quando o User se torna superuser."""
    
    # 1. Verifica o estado inicial (deve ser 'Cliente')
    perfil = usuario_cliente.perfil
    assert perfil.tipoUsuario == 'Cliente'
    
    # 2. Ação: Promove o usuário a superuser e salva (dispara o sinal)
    usuario_cliente.is_superuser = True
    usuario_cliente.save()
    
    # Recarrega o perfil do banco para pegar as mudanças
    perfil.refresh_from_db() 
    
    # 3. Assert: Verifica se o tipo foi atualizado pelo sinal
    assert perfil.tipoUsuario == 'Administrador'

@pytest.mark.django_db
def test_perfilusuario_sincronizacao_rebaixamento(usuario_admin):
    """Verifica se o tipoUsuario muda de volta para 'Cliente' quando o superuser é rebaixado."""
    
    # 1. Verifica o estado inicial (deve ser 'Administrador')
    perfil = usuario_admin.perfil
    assert perfil.tipoUsuario == 'Administrador'
    
    # 2. Ação: Rebaixa o usuário e salva (dispara o sinal)
    usuario_admin.is_superuser = False
    usuario_admin.save()
    
    # Recarrega o perfil do banco para pegar as mudanças
    perfil.refresh_from_db()
    
    # 3. Assert: Verifica se o tipo foi atualizado para 'Cliente'
    assert perfil.tipoUsuario == 'Cliente'

# ===================================================================
# TESTES PARA selfcare_models.Habito
# ===================================================================

@pytest.mark.django_db
def test_habito_criacao(habito_exemplo, usuario_cliente):
    """Verifica a criação básica de um Hábito e seus campos."""
    
    habito = habito_exemplo
    
    assert habito.usuario == usuario_cliente
    assert habito.nome == "Beber Água"
    assert habito.quantidade == 8
    assert habito.frequencia == 'DIARIO'
    assert str(habito) == "Beber Água"

@pytest.mark.django_db
def test_habito_relacionamento_usuario(usuario_cliente):
    """Verifica se o relacionamento reverso do User para Habito funciona."""
    
    Habito.objects.create(
        usuario=usuario_cliente,
        nome="Meditar",
        data_inicio=date.today(),
        quantidade=15,
        frequencia=Habito.DIARIO
    )
    
    # Verifica o related_name='habitos'
    assert usuario_cliente.habitos.count() == 1
    assert usuario_cliente.habitos.first().nome == "Meditar"

# ===================================================================
# TESTES PARA selfcare_models.StatusDiario (Unique Constraint)
# ===================================================================

@pytest.mark.django_db
def test_statusdiario_criacao_sucesso(habito_exemplo):
    """Verifica a criação bem-sucedida de um StatusDiario."""
    
    status = StatusDiario.objects.create(
        habito=habito_exemplo,
        data=date.today(),
        concluido=True
    )
    
    assert status.concluido is True
    assert status.data == date.today()
    assert 'Concluído' in str(status)

@pytest.mark.django_db
def test_statusdiario_unique_together_falha(habito_exemplo):
    """Verifica a falha ao tentar criar dois StatusDiario para o mesmo Hábito e Data."""
    
    # Cria o primeiro registro (sucesso)
    StatusDiario.objects.create(
        habito=habito_exemplo,
        data=date.today(),
        concluido=True
    )
    
    # Tenta criar o segundo registro com a mesma chave única (habito, data)
    with pytest.raises(IntegrityError):
        StatusDiario.objects.create(
            habito=habito_exemplo,
            data=date.today(),
            concluido=False # Concluido diferente, mas a chave é a mesma
        )

# ===================================================================
# TESTES PARA selfcare_models.HumorTipo e Humor (FK e Unique Constraint)
# ===================================================================

@pytest.mark.django_db
def test_humortipo_criacao(humor_tipo_feliz):
    """Verifica a criação básica de um HumorTipo."""
    
    assert humor_tipo_feliz.estado == "Feliz"
    assert HumorTipo.objects.count() == 1

@pytest.mark.django_db
def test_humor_criacao_sucesso(usuario_cliente, humor_tipo_feliz):
    """Verifica a criação bem-sucedida de um registro de Humor."""
    
    registro_humor = Humor.objects.create(
        usuario=usuario_cliente,
        data=date.today(),
        estado=humor_tipo_feliz,
        descricaohumor="Tive um ótimo dia de trabalho!"
    )
    
    assert registro_humor.usuario == usuario_cliente
    assert registro_humor.estado.estado == "Feliz"
    assert registro_humor.data == date.today()
    assert str(registro_humor) == f"{usuario_cliente.username} - {date.today()} - Feliz"
    
@pytest.mark.django_db
def test_humor_unique_together_falha(usuario_cliente, humor_tipo_feliz):
    """Verifica a falha ao tentar criar dois registros de Humor para o mesmo Usuário e Data."""
    
    # Cria o primeiro registro
    Humor.objects.create(
        usuario=usuario_cliente,
        data=date.today(),
        estado=humor_tipo_feliz,
    )
    
    # Tenta criar o segundo registro com a mesma chave única (usuario, data)
    with pytest.raises(IntegrityError):
        Humor.objects.create(
            usuario=usuario_cliente,
            data=date.today(),
            estado=humor_tipo_feliz,
        )

# ===================================================================
# TESTES PARA outros Models
# ===================================================================

@pytest.mark.django_db
def test_devicetoken_criacao_sucesso(usuario_cliente):
    """Verifica a criação e as chaves únicas de DeviceToken."""
    
    token = DeviceToken.objects.create(
        user=usuario_cliente,
        token='um_token_unico_12345',
        device_type='android'
    )
    
    assert token.user == usuario_cliente
    
    # Verifica a falha ao tentar usar o mesmo token
    with pytest.raises(IntegrityError):
         DeviceToken.objects.create(
            user=usuario_cliente,
            token='um_token_unico_12345',
            device_type='ios' # Mesmo token, falha
        )