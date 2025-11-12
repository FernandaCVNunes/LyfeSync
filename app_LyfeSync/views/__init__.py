# app_LyfeSync/views/__init__.py

# Views Públicas (public_views.py)
from .public_views import (
    home, sobre_nos, contatos, login_view, cadastro, logout_view
)

# Views de Hábito (habit_views.py)
from .habit_views import (
    home_lyfesync, habito, marcar_habito_concluido, registrar_habito, 
    alterar_habito, toggle_habito_day, delete_habit
)

# Views de Autocuidado (selfcare_views.py)
from .selfcare_views import (
    autocuidado, humor, registrar_humor, alterar_humor, load_humor_by_date, 
    gratidao, registrar_gratidao, alterar_gratidao, delete_gratidao, 
    afirmacao, registrar_afirmacao, alterar_afirmacao, delete_afirmacao
)

# Views de Relatórios (report_views.py)
from .report_views import (
    relatorios, relatorio_habito, relatorio_humor, 
    relatorio_gratidao, relatorio_afirmacao
)

# Views de Conta/Configurações (config_views.py)
from .config_views import (
    conta, configuracoes_conta
)

# Views Administrativas (admin_views.py)
from .admin_views import (
    registrar_dica
)