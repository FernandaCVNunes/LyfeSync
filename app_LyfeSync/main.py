# app_LyfeSync/main.py
# Ficheiro principal de execução ou ponto de inicialização da aplicação LyfeSync.

# Importa as configurações globais da aplicação
from app_LyfeSync.config import MOOD_CHOICES, DEFAULT_USER_TYPE
# Importa a lógica auxiliar de mapeamento visual
from app_LyfeSync.views._aux.logic import get_humor_map

def run_app_initialization():
    """
    Função para simular a inicialização da aplicação, carregando
    as configurações e verificando a lógica de mapeamento.
    """
    print("--- Inicialização da Aplicação LyfeSync ---")
    print(f"Tipo de Utilizador Padrão: {DEFAULT_USER_TYPE}")
    
    # 1. Testar as opções de humor do Modelo de Dados (BD)
    print("\n[CONFIGURAÇÃO DE HUMOR - BASE DE DADOS]")
    print("MOOD_CHOICES (ID, Rótulo) para uso em models.py:")
    for id_value, label in MOOD_CHOICES:
        print(f"  ID: {id_value}, Rótulo: {label}")
        
    # 2. Testar o mapeamento de humor para os ícones estáticos
    humor_map = get_humor_map()
    print("\n[MAPA DE HUMOR - LÓGICA DE APRESENTAÇÃO]")
    print("Mapeamento (Rótulo -> Caminho do Ícone) para uso em templates:")
    
    # Simular a obtenção de um registo do BD e o mapeamento para o ícone
    for label, icon_path in humor_map.items():
        # Encontra o ID correspondente na lista MOOD_CHOICES
        id_value = next((id_val for id_val, lbl in MOOD_CHOICES if lbl == label), 'N/A')
        print(f"  ID BD: {id_value} | Rótulo: '{label}' -> Ícone: '{icon_path}'")

    print("\nInicialização concluída. As configurações e a lógica de mapeamento estão consistentes.")


if __name__ == "__main__":
    # Garante que a função de inicialização é executada quando o script é chamado diretamente
    run_app_initialization()
