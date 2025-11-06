import os
import sys

# Diretórios para ignorar (evita erros e lentidão)
EXCLUDE_DIRS = [
    '.git',
    '__pycache__',
    # IMPORTANTE: Descomente 'venv' SE quiser verificar se o problema está em um arquivo de biblioteca
    # 'venv' 
]

# Definindo a raiz do projeto para escanear
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))

def scan_for_null_bytes(root_dir):
    """Escaneia todos os arquivos .py no projeto em busca de bytes nulos."""
    print(f"--- Escaneando a partir da raiz: {root_dir} ---")
    found_issue = False
    
    for root, dirs, files in os.walk(root_dir, topdown=True):
        # Excluir diretórios
        dirs[:] = [d for d in dirs if d not in EXCLUDE_DIRS]
        
        for file_name in files:
            if file_name.endswith('.py'):
                file_path = os.path.join(root, file_name)
                
                # Ignorar arquivos do venv, a menos que o problema persista
                if 'venv' in root.split(os.sep) and 'venv' not in EXCLUDE_DIRS:
                    continue

                try:
                    # Abrindo em modo binário para detectar o byte nulo
                    with open(file_path, 'rb') as f:
                        content = f.read()
                        # Verificar se o byte nulo '\x00' está no conteúdo
                        if b'\x00' in content:
                            print(f"[ERRO GRAVE ENCONTRADO] O arquivo contém byte nulo: {file_path}")
                            found_issue = True
                except Exception as e:
                    # Em caso de erro de permissão ou outro problema de I/O
                    print(f"Erro ao ler o arquivo {file_path}: {e}")

    if not found_issue:
        print("\nNENHUM byte nulo encontrado nos arquivos .py do seu código-fonte.")
    
    return found_issue

if __name__ == "__main__":
    if scan_for_null_bytes(PROJECT_ROOT):
        print("\n*** Ação necessária: Abra o arquivo listado e delete o caractere \x00. ***")
    else:
        print("\nO problema PODE estar nas bibliotecas do venv ou em um arquivo não-Python.")