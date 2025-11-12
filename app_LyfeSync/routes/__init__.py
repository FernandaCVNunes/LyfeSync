# Este ficheiro transforma a pasta 'routes' num pacote Python importável.

# Aqui, importamos os padrões de URL definidos nos sub-ficheiros de rotas.
# O objetivo é expor uma lista combinada de urlpatterns para o urls.py principal da aplicação.

from .auth_routes import urlpatterns as auth_patterns
from .dashboard_routes import urlpatterns as dashboard_patterns
from .mood_routes import urlpatterns as mood_patterns
from .journal_routes import urlpatterns as journal_patterns
from .habit_routes import urlpatterns as habit_patterns
from .task_routes import urlpatterns as task_patterns

# Cria uma lista de padrões de URL combinados para serem importados no ficheiro urls.py da app.
urlpatterns = (
    auth_patterns +
    dashboard_patterns +
    mood_patterns +
    journal_patterns +
    habit_patterns +
    task_patterns
)
