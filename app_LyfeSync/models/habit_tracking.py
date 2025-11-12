# habit_tracking.py
# Modelos para definição e acompanhamento de hábitos diários/recorrentes.

from django.db import models
from django.conf import settings
from datetime import date

class Habit(models.Model):
    """
    Define um Hábito a ser rastreado pelo usuário.
    """
    FREQUENCY_CHOICES = [
        ('daily', 'Diariamente'),
        ('weekly', 'Semanalmente'),
        ('monthly', 'Mensalmente'),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='habits',
        verbose_name='Usuário'
    )
    name = models.CharField(
        max_length=150,
        verbose_name='Nome do Hábito'
    )
    description = models.TextField(
        blank=True,
        verbose_name='Descrição'
    )
    frequency = models.CharField(
        max_length=20,
        choices=FREQUENCY_CHOICES,
        default='daily',
        verbose_name='Frequência'
    )
    start_date = models.DateField(
        default=date.today,
        verbose_name='Data de Início'
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name='Ativo'
    )

    class Meta:
        verbose_name = 'Hábito'
        verbose_name_plural = 'Hábitos'
        unique_together = ('user', 'name',) # Um usuário não pode ter dois hábitos com o mesmo nome

    def __str__(self):
        return f'{self.name} ({self.user.username})'

class HabitLog(models.Model):
    """
    Registro diário da conclusão de um Hábito.
    """
    STATUS_CHOICES = [
        ('completed', 'Concluído'),
        ('skipped', 'Ignorado'),
        ('failed', 'Falhou/Perdeu'),
    ]

    habit = models.ForeignKey(
        Habit,
        on_delete=models.CASCADE,
        related_name='logs',
        verbose_name='Hábito'
    )
    log_date = models.DateField(
        verbose_name='Data do Registro',
        default=date.today
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='completed',
        verbose_name='Status'
    )

    class Meta:
        verbose_name = 'Registro de Hábito'
        verbose_name_plural = 'Registros de Hábitos'
        unique_together = ('habit', 'log_date',) # Apenas um registro por hábito por dia
        ordering = ['-log_date']

    def __str__(self):
        return f'{self.habit.name} - {self.log_date} ({self.status})'