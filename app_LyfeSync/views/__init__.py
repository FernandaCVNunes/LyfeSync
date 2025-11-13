# app_LyfeSync/views/__init__.py

# Este arquivo agrega todas as views para que possam ser importadas centralizadamente

# Views Públicas (public_views.py)
# Adicione aqui todas as suas importações de public_views
from .public_views import (
    home, sobre_nos, contatos, login_view, cadastro, logout_view
)

# Views de Hábito (habit_views.py)
# Garante que TODAS as funções de hábitos, incluindo as novas, sejam exportadas.
from .habit_views import (
    home_lyfesync,         # Necessário para 'homeLyfesync'
    habito,
    registrar_habito,
    alterar_habito,
    toggle_habito_day,
    delete_habit,
    get_habit_data,        # <--- Esta é a view que estava faltando ser exportada!
)

# Views de Autocuidado (selfcare_views.py)
# Adicione aqui todas as suas importações de selfcare_views
from .selfcare_views import (
    autocuidado, humor, registrar_humor, alterar_humor, load_humor_by_date, 
    gratidao, registrar_gratidao, alterar_gratidao, 
    afirmacao, registrar_afirmacao, alterar_afirmacao
)

# Views de Relatórios (report_views.py)
# Adicione aqui todas as suas importações de report_views
from .report_views import (
    relatorios, relatorio_habito, relatorio_humor, 
    relatorio_gratidao, relatorio_afirmacao
)

# Views de Conta/Configurações (config_views.py)
# Adicione aqui todas as suas importações de config_views
from .config_views import (
    conta, configuracoes_conta
)

# Views Administrativas (admin_views.py)
# Adicione aqui todas as suas importações de admin_views
from .admin_views import (
    registrar_dica
)