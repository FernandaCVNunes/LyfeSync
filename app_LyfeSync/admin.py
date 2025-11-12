#admin.py#
from django.contrib import admin
from .models import (
    # Usuário e Perfil
    UserProfile, UserNotificationSettings, DeviceToken,
    # Tarefas
    Task, TaskCategory,
    # Hábitos
    Habit, HabitLog, HabitStreak,
    # Humor e Diário
    MoodEntry, JournalEntry,
    # Utilities
    ActivityLog, SystemConfiguration
)

# --- 1. Modelos de Usuário e Perfil ---

class UserProfileAdmin(admin.ModelAdmin):
    """Configuração para o modelo UserProfile."""
    list_display = ('user', 'gender', 'birth_date', 'timezone', 'created_at', 'last_updated')
    search_fields = ('user__username', 'user__email')
    list_filter = ('gender', 'timezone')
    readonly_fields = ('created_at', 'last_updated')

class UserNotificationSettingsAdmin(admin.ModelAdmin):
    """Configuração para as preferências de notificação do usuário."""
    list_display = ('user', 'email_notifications', 'in_app_reminders', 'last_updated')
    search_fields = ('user__username', 'user__email')
    list_filter = ('email_notifications', 'in_app_reminders')
    readonly_fields = ('last_updated',)

class DeviceTokenAdmin(admin.ModelAdmin):
    """Configuração para os tokens de dispositivo para notificações push."""
    list_display = ('user', 'device_type', 'token', 'created_at')
    search_fields = ('user__username', 'token')
    list_filter = ('device_type',)
    readonly_fields = ('created_at',)


# --- 2. Modelos de Tarefas (Tasks) ---

class TaskCategoryAdmin(admin.ModelAdmin):
    """Configuração para as categorias de tarefas."""
    list_display = ('name', 'user', 'color_code', 'created_at')
    search_fields = ('name', 'user__username')
    readonly_fields = ('created_at',)

class TaskAdmin(admin.ModelAdmin):
    """Configuração para o modelo Task."""
    list_display = ('title', 'user', 'category', 'due_date', 'priority', 'is_completed')
    search_fields = ('title', 'user__username')
    list_filter = ('is_completed', 'priority', 'category')
    date_hierarchy = 'due_date'
    readonly_fields = ('created_at', 'completed_at')


# --- 3. Modelos de Hábitos (Habit Tracking) ---

class HabitAdmin(admin.ModelAdmin):
    """Configuração para o modelo Habit."""
    list_display = ('name', 'user', 'frequency', 'start_date', 'current_streak', 'is_active')
    search_fields = ('name', 'user__username')
    list_filter = ('is_active', 'frequency')
    date_hierarchy = 'start_date'
    readonly_fields = ('created_at', 'current_streak', 'longest_streak')

class HabitLogAdmin(admin.ModelAdmin):
    """Configuração para os registos diários de hábitos."""
    list_display = ('habit', 'log_date', 'is_completed', 'notes')
    search_fields = ('habit__name', 'notes')
    list_filter = ('is_completed',)
    date_hierarchy = 'log_date'
    raw_id_fields = ('habit',) # Útil para procurar hábitos em bases de dados grandes

class HabitStreakAdmin(admin.ModelAdmin):
    """Configuração para as sequências de hábitos (streaks)."""
    list_display = ('habit', 'start_date', 'end_date', 'days_count', 'is_current')
    list_filter = ('is_current',)
    date_hierarchy = 'start_date'
    readonly_fields = ('start_date', 'end_date', 'days_count')


# --- 4. Modelos de Humor e Diário (Mood and Journals) ---

class MoodEntryAdmin(admin.ModelAdmin):
    """Configuração para o registo de humor."""
    list_display = ('user', 'mood_level', 'recorded_at', 'notes')
    search_fields = ('user__username', 'notes')
    list_filter = ('mood_level',)
    date_hierarchy = 'recorded_at'
    readonly_fields = ('recorded_at',)

class JournalEntryAdmin(admin.ModelAdmin):
    """Configuração para as entradas de diário."""
    list_display = ('user', 'title', 'created_at', 'last_updated')
    search_fields = ('user__username', 'title', 'content')
    date_hierarchy = 'created_at'
    readonly_fields = ('created_at', 'last_updated')


# --- 5. Modelos de Utilities (Admin) ---

class ActivityLogAdmin(admin.ModelAdmin):
    """Configuração para o registo de atividades do sistema."""
    list_display = ('user', 'action', 'timestamp', 'ip_address')
    search_fields = ('user__username', 'action')
    list_filter = ('action',)
    date_hierarchy = 'timestamp'
    readonly_fields = ('user', 'action', 'timestamp', 'ip_address')

class SystemConfigurationAdmin(admin.ModelAdmin):
    """Configuração para as configurações globais do sistema."""
    list_display = ('key', 'value', 'data_type', 'last_updated')
    search_fields = ('key', 'value')
    list_filter = ('data_type',)
    readonly_fields = ('last_updated',)


# --- Registo Final dos Modelos ---

admin.site.register(UserProfile, UserProfileAdmin)
admin.site.register(UserNotificationSettings, UserNotificationSettingsAdmin)
admin.site.register(DeviceToken, DeviceTokenAdmin)

admin.site.register(TaskCategory, TaskCategoryAdmin)
admin.site.register(Task, TaskAdmin)

admin.site.register(Habit, HabitAdmin)
admin.site.register(HabitLog, HabitLogAdmin)
admin.site.register(HabitStreak, HabitStreakAdmin)

admin.site.register(MoodEntry, MoodEntryAdmin)
admin.site.register(JournalEntry, JournalEntryAdmin)

admin.site.register(ActivityLog, ActivityLogAdmin)
admin.site.register(SystemConfiguration, SystemConfigurationAdmin)