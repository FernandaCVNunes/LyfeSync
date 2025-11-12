# __init__.py no diretório 'models'
# Este arquivo garante que todos os modelos definidos nos arquivos separados
# sejam importados e registrados no sistema de modelos do Django.

# Importa modelos do user.py
from .user import CustomUser

# Importa modelos do user_profile_and_signals.py
from .user_profile_and_signals import UserProfile, UserNotificationSettings

# Importa modelos do habit_tracking.py
# CORREÇÃO: Adicionando HabitStreak
from .habit_tracking import Habit, HabitLog, HabitStreak

# Importa modelos do mood_and_journals.py
from .mood_and_journals import MoodEntry, JournalEntry

# Importa modelos do task.py
from .task import TaskCategory, Task

# Importa modelos do system_externals.py
from .system_externals import ExternalIntegrationSetting

# Importa modelos de gerenciamento de dispositivos
from .device_management import DeviceToken

# NOVO: Importa modelos de utilidades/admin
from .system_utilities import ActivityLog, SystemConfiguration

# Nota: O admin_utilities.py não é importado aqui porque contém apenas
# configurações para o painel de administração, e não definições de modelos.

# Opcional: define quais símbolos são exportados quando um 'import *' é feito
__all__ = [
    'CustomUser',
    'UserProfile',
    'UserNotificationSettings', 
    'DeviceToken', # Adicionado
    'Habit',
    'HabitLog',
    'HabitStreak', # Adicionado
    'MoodEntry',
    'JournalEntry',
    'TaskCategory',
    'Task',
    'ExternalIntegrationSetting',
    'ActivityLog', # Adicionado
    'SystemConfiguration', # Adicionado
]