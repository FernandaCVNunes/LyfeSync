#models/__init__.py

from .auth_models import *

# Importa todas as classes e constantes definidas em selfcare_models.py
from .selfcare_models import *

# Re-define o User do Django aqui, para garantir que ele esteja disponível
# quando outros arquivos importam 'from .models import User'
from django.contrib.auth import get_user_model
User = get_user_model()