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
#   VIEWS PÚBLICAS
# -------------------------------------------------------------------
from .public_views import (
    home,
    sobre_nos,
    contatos
)

# -------------------------------------------------------------------
#   VIEWS DE CONFIGURAÇÃO
# -------------------------------------------------------------------
from .config_views import (
    conta, 
    configuracoes_conta,
    excluir_conta
)

# -------------------------------------------------------------------
#   VIEWS DE AUTOCUIDADO
# -------------------------------------------------------------------

from .selfcare_views import (
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
#   VIEWS DE HÁBITOS E DASHBOARD
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
#   VIEWS DE RELATÓRIO
# -------------------------------------------------------------------
from .reports_views import (
    relatorios,
    relatorio,
    relatorio_habito,
    relatorio_gratidao,
    relatorio_afirmacao,
    relatorio_humor,
    exportar_habito_csv,
    exportar_habito_pdf,
    exportar_gratidao_csv,
    exportar_afirmacao_csv,
    exportar_gratidao_pdf,
    exportar_afirmacao_pdf,
    exportar_humor_csv,
    exportar_humor_pdf
)