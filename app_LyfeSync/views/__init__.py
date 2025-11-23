# app_LyfeSync/views/__init__.py

# -------------------------------------------------------------------
# LÓGICA AUXILIAR
# -------------------------------------------------------------------
from ._aux_logic import (
    _get_report_date_range,
    get_humor_map,
    _get_humor_cor_classe,
    _get_checked_days_for_last_7_days,
    get_habitos_e_acompanhamento,
    Humor_mock,
    extract_dica_info, 
    rebuild_descricaohumor, 
)

# -------------------------------------------------------------------
# 1. VIEWS PÚBLICAS
# -------------------------------------------------------------------
from .public_views import (
    home,
    sobre_nos,
    contatos
)

# -------------------------------------------------------------------
# 2. VIEWS DE CONFIGURAÇÃO (Conta e Segurança)
# -------------------------------------------------------------------
from .config_views import (
    conta, 
    configuracoes_conta,
    excluir_conta
)

# -------------------------------------------------------------------
# 3. VIEWS DE ADMIN (Dicas)
# -------------------------------------------------------------------
# Dicas é uma função duplicada, vamos renomear a versão de admin para evitar conflito.
from .admin_views import (
    registrar_dica as admin_registrar_dica, alterar_dica, excluir_dica,
)

# -------------------------------------------------------------------
# 4. VIEWS DE AUTOCUIDADO/CRUD (Humor, Gratidão, Afirmação, Dicas)
# -------------------------------------------------------------------
from .selfcare_views import (
    is_staff_user, # Função de teste de autorização
    autocuidado,
    
    # Humor
    humor,
    registrar_humor,
    alterar_humor,
    delete_humor,
    load_humor_by_date,
    
    # Dicas (Admin/Staff via selfcare_views.py)
    registrar_dica,
    alterar_dica, 
    excluir_dica,

    
    # Gratidão
    gratidao,
    registrar_gratidao,
    alterar_gratidao,
    delete_gratidao,
    
    # Afirmação
    afirmacao,
    registrar_afirmacao,
    alterar_afirmacao,
    delete_afirmacao
)

from .crud_views import (
    is_staff_user, 
    autocuidado,
    
    # Humor
    humor,
    registrar_humor,
    alterar_humor,
    delete_humor,
    load_humor_by_date,
    
    # Dicas
    registrar_dica,
    alterar_dica, 
    excluir_dica,

    
    # Gratidão
    gratidao,
    registrar_gratidao,
    alterar_gratidao,
    delete_gratidao,
    
    # Afirmação
    afirmacao,
    registrar_afirmacao,
    alterar_afirmacao,
    delete_afirmacao
)

# -------------------------------------------------------------------
# 5. VIEWS DE HÁBITOS E DASHBOARD
# -------------------------------------------------------------------
from .habit_views import (
    home_lyfesync,
    habito,
    registrar_habito,
    alterar_habito,
    get_habit_data,
    toggle_habito_day,
    delete_habit
)

# -------------------------------------------------------------------
# 6. VIEWS DE EXPORTAÇÃO
# -------------------------------------------------------------------
from .exports_views import (
    exportar_habito_csv,
    exportar_habito_pdf,
    exportar_gratidao_csv,
    exportar_afirmacao_csv,
    exportar_gratidao_pdf,
    exportar_afirmacao_pdf,
    exportar_humor_csv,
    exportar_humor_pdf
)

# -------------------------------------------------------------------
# 7. VIEWS DE RELATÓRIO
# -------------------------------------------------------------------
from .reports_views import (
    relatorios,
    relatorio,
    relatorio_habito,
    relatorio_gratidao,
    relatorio_afirmacao,
    relatorio_humor
)