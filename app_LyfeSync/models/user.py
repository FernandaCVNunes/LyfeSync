# user.py
# Modelo de usuário personalizado para o sistema.

from django.db import models
from django.contrib.auth.models import AbstractUser

class CustomUser(AbstractUser):
    """
    Modelo de Usuário personalizado que estende o AbstractUser do Django.
    Pode-se adicionar campos específicos aqui que não estão no modelo base.
    """
    # Adicionando um campo simples como exemplo
    date_of_birth = models.DateField(
        null=True,
        blank=True,
        verbose_name='Data de Nascimento'
    )
    is_premium = models.BooleanField(
        default=False,
        verbose_name='Conta Premium'
    )
    # Você pode manter o `username`, `email`, `first_name`, `last_name` padrão
    # ou ajustá-los se necessário.

    class Meta:
        verbose_name = 'Usuário do Sistema'
        verbose_name_plural = 'Usuários do Sistema'
        db_table = 'custom_user' # Garante um nome de tabela específico

    def __str__(self):
        return self.email or self.username