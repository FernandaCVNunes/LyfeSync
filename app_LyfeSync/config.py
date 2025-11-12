# app_LyfeSync/config.py
# Este arquivo armazena constantes e parâmetros de configuração específicos
# da aplicação LyfeSync, separados do settings.py global.

# --- Configurações de Usuário e Assinatura ---

# Opções de tipo de usuário, usadas no modelo UserProfile
USER_TYPE_CHOICES = (
    ('BASIC', 'Básico'),
    ('PREMIUM', 'Premium'),
    ('ADMIN', 'Administrador'),
)
# Tipo de usuário padrão para novos registros
DEFAULT_USER_TYPE = 'BASIC'

# --- Configurações de Tarefas e Categorias ---

# Limite máximo de tarefas ativas (para todos os usuários)
MAX_TASKS_PER_USER = 50 

# Cores padrão disponíveis para categorias (em formato HEX)
DEFAULT_COLOR_CODES = {
    'SAUDE': '#34D399',      # Verde (Health)
    'TRABALHO': '#60A5FA',   # Azul (Work)
    'PESSOAL': '#FCD34D',    # Amarelo (Personal)
    'URGENTE': '#F87171',    # Vermelho (Urgent)
}


# --- Configurações de Hábitos ---

# Limite máximo de hábitos ativos que um usuário Básico pode ter
MAX_HABITS_BASIC_USER = 5

# Quantidade mínima de dias para ser considerado um "Super Streak"
SUPER_STREAK_THRESHOLD = 30
# Frequência padrão de notificação de lembrete (em dias)
DEFAULT_REMINDER_FREQUENCY_DAYS = 1


# --- Configurações de Humor (MOOD_CHOICES) ---

# Definição dos níveis de humor em formato CHOICES para uso em models.py
# Estes rótulos devem corresponder aos usados na função get_humor_map().
# Formato: (valor_no_BD, 'Rótulo_Legível')
MOOD_CHOICES = [
    (1, 'Irritado'),
    (2, 'Triste'),
    (3, 'Ansioso'),
    (4, 'Calmo'),
    (5, 'Feliz'),
]


# --- Mensagens Padrão ---

# Mensagem de boas-vindas para novos usuários
WELCOME_MESSAGE = "Bem-vindo(a) ao LyfeSync! Comece a acompanhar seus hábitos hoje."
