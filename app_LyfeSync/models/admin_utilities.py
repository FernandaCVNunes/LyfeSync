# admin_utilities.py
# Configuração do painel de administração para registrar todos os modelos.
# Isso não é um modelo, mas uma parte essencial da "camada de modelos" no Django
# para gerenciamento de dados.

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

# Importa todos os modelos definidos anteriormente
from .user import CustomUser
from .user_profile_and_signals import UserProfile
from .habit_tracking import Habit, HabitLog
from .mood_and_journals import MoodEntry, JournalEntry
from .task import TaskCategory, Task
from .system_externals import ExternalIntegrationSetting

# --- 1. Admin para CustomUser e Perfil ---

class CustomUserAdmin(BaseUserAdmin):
    """Admin personalizado para o CustomUser."""
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'is_premium')
    fieldsets = BaseUserAdmin.fieldsets + (
        (None, {'fields': ('date_of_birth', 'is_premium')}),
    )
    list_filter = BaseUserAdmin.list_filter + ('is_premium',)

class UserProfileInline(admin.StackedInline):
    """Inline para exibir o Perfil ao editar o Usuário."""
    model = UserProfile
    can_delete = False
    verbose_name_plural = 'Perfil'

@admin.register(CustomUser)
class CustomUserWithProfileAdmin(CustomUserAdmin):
    """Registra CustomUser com o perfil inline."""
    inlines = (UserProfileInline,)

# --- 2. Administração de Hábitos ---

@admin.register(Habit)
class HabitAdmin(admin.ModelAdmin):
    list_display = ('name', 'user', 'frequency', 'start_date', 'is_active')
    list_filter = ('frequency', 'is_active', 'start_date')
    search_fields = ('name', 'user__username')

@admin.register(HabitLog)
class HabitLogAdmin(admin.ModelAdmin):
    list_display = ('habit', 'log_date', 'status')
    list_filter = ('status', 'log_date')
    search_fields = ('habit__name', 'habit__user__username')

# --- 3. Administração de Humor e Diário ---

@admin.register(MoodEntry)
class MoodEntryAdmin(admin.ModelAdmin):
    list_display = ('user', 'entry_date', 'rating', 'created_at')
    list_filter = ('rating', 'entry_date')
    search_fields = ('user__username', 'notes')

@admin.register(JournalEntry)
class JournalEntryAdmin(admin.ModelAdmin):
    list_display = ('title', 'user', 'entry_date', 'is_private')
    list_filter = ('is_private', 'entry_date')
    search_fields = ('title', 'content', 'user__username')

# --- 4. Administração de Tarefas ---

@admin.register(TaskCategory)
class TaskCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'user', 'color_hex')
    search_fields = ('name', 'user__username')

@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ('title', 'user', 'category', 'due_date', 'priority', 'is_completed')
    list_filter = ('is_completed', 'priority', 'due_date', 'category')
    search_fields = ('title', 'description', 'user__username')

# --- 5. Administração de Externals ---

@admin.register(ExternalIntegrationSetting)
class ExternalIntegrationSettingAdmin(admin.ModelAdmin):
    list_display = ('api_name', 'user', 'is_active', 'last_synced')
    list_filter = ('is_active', 'api_name')
    search_fields = ('api_name', 'user__username')