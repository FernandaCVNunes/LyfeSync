# task.py
# Modelos para gestão de tarefas e To-Do List.

from django.db import models
from django.conf import settings
from datetime import date

# Nota de correção: Não é necessário importar TaskCategory ou Task de .task aqui,
# pois elas estão sendo definidas neste mesmo arquivo.

class TaskCategory(models.Model):
    """
    Categorias para organizar tarefas (ex: Trabalho, Pessoal, Fitness).
    """
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='task_categories',
        verbose_name='Usuário'
    )
    name = models.CharField(
        max_length=100,
        verbose_name='Nome da Categoria'
    )
    color_hex = models.CharField(
        max_length=7,
        default='#000000',
        verbose_name='Cor de Identificação'
    )

    class Meta:
        verbose_name = 'Categoria de Tarefa'
        verbose_name_plural = 'Categorias de Tarefas'
        unique_together = ('user', 'name',)

    def __str__(self):
        return self.name

class Task(models.Model):
    """
    Modelo de Tarefa individual.
    """
    PRIORITY_CHOICES = [
        (1, 'Baixa'),
        (2, 'Média'),
        (3, 'Alta'),
        (4, 'Urgente'),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='tasks',
        verbose_name='Usuário'
    )
    category = models.ForeignKey(
        TaskCategory,
        on_delete=models.SET_NULL, # Mantém a tarefa se a categoria for excluída
        null=True,
        blank=True,
        related_name='tasks',
        verbose_name='Categoria'
    )
    title = models.CharField(
        max_length=200,
        verbose_name='Título da Tarefa'
    )
    description = models.TextField(
        blank=True,
        verbose_name='Detalhes'
    )
    due_date = models.DateField(
        null=True,
        blank=True,
        verbose_name='Data de Vencimento'
    )
    priority = models.IntegerField(
        choices=PRIORITY_CHOICES,
        default=2,
        verbose_name='Prioridade'
    )
    is_completed = models.BooleanField(
        default=False,
        verbose_name='Concluída'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Criado Em'
    )
    completed_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='Concluído Em'
    )

    class Meta:
        verbose_name = 'Tarefa'
        verbose_name_plural = 'Tarefas'
        ordering = ['priority', 'due_date', 'title'] # Ordenação padrão: por prioridade, depois data

    def __str__(self):
        return self.title