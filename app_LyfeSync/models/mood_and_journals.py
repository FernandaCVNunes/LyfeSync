# mood_and_journals.py
# Modelos para rastreamento de humor e entradas de diário (journals).

from django.db import models
from django.conf import settings
from datetime import date

# --- Modelos de Humor ---

class MoodEntry(models.Model):
    """
    Registro diário do humor do usuário.
    """
    MOOD_CHOICES = [
        (1, 'Péssimo'),
        (2, 'Ruim'),
        (3, 'Neutro'),
        (4, 'Bom'),
        (5, 'Excelente'),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='mood_entries',
        verbose_name='Usuário'
    )
    entry_date = models.DateField(
        default=date.today,
        verbose_name='Data do Registro'
    )
    rating = models.IntegerField(
        choices=MOOD_CHOICES,
        verbose_name='Classificação do Humor (1-5)'
    )
    notes = models.TextField(
        blank=True,
        verbose_name='Observações'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Criado Em'
    )

    class Meta:
        verbose_name = 'Registro de Humor'
        verbose_name_plural = 'Registros de Humor'
        unique_together = ('user', 'entry_date',) # Apenas um registro de humor por dia
        ordering = ['-entry_date']

    def __str__(self):
        return f'Humor de {self.user.username} em {self.entry_date}: {self.get_rating_display()}'

# --- Modelos de Diário ---

class JournalEntry(models.Model):
    """
    Entrada de diário ou registro de pensamento.
    """
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='journal_entries',
        verbose_name='Usuário'
    )
    title = models.CharField(
        max_length=200,
        verbose_name='Título'
    )
    content = models.TextField(
        verbose_name='Conteúdo do Diário'
    )
    entry_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Data e Hora da Entrada'
    )
    is_private = models.BooleanField(
        default=True,
        verbose_name='Privado'
    )

    class Meta:
        verbose_name = 'Entrada de Diário'
        verbose_name_plural = 'Entradas de Diário'
        ordering = ['-entry_date']

    def __str__(self):
        return f'{self.title} por {self.user.username} em {self.entry_date.date()}'