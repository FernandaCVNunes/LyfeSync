from datetime import date
from typing import List, Dict, Any, Optional

# PLACEHOLDER: Usamos classes fictícias para simular o Modelo (JournalEntry)
class MockJournalEntry:
    """Classe fictícia para simular o modelo de Entrada de Diário (JournalEntry)."""
    def __init__(self, entry_id: int, user_id: int, content: str, entry_date: date, tags: List[str] = None):
        self.id = entry_id
        self.user_id = user_id
        self.content = content
        self.entry_date = entry_date
        self.tags = tags if tags is not None else []

# Dicionário fictício para simular a base de dados de entradas de diário
mock_journal_db: List[MockJournalEntry] = [
    MockJournalEntry(1, 1, "Hoje senti-me muito grato pela conversa com um amigo. É importante manter estas ligações.", date.today()),
    MockJournalEntry(2, 1, "Análise do progresso no projeto 'Falcão'. Algum stress, mas no bom caminho.", date.today() - timedelta(days=2), tags=['trabalho', 'progresso']),
    MockJournalEntry(3, 2, "Dia calmo, passei a tarde a ler e a relaxar.", date.today() - timedelta(days=1)),
]

class JournalService:
    """
    Encapsula a lógica de negócio para a gestão de entradas de diário,
    incluindo a criação, recuperação por data e pesquisa por conteúdo/tags.
    """

    def __init__(self):
        self.next_id = len(mock_journal_db) + 1
        pass

    def create_entry(self, user_id: int, content: str, tags: List[str] = None) -> MockJournalEntry:
        """
        Cria uma nova entrada de diário para o dia de hoje.
        """
        current_date = date.today()
        print(f"A criar nova entrada de diário para o utilizador {user_id} em {current_date}.")
        
        # Lógica real: JournalEntry.objects.create(...)
        new_entry = MockJournalEntry(self.next_id, user_id, content, current_date, tags)
        mock_journal_db.append(new_entry)
        self.next_id += 1
        return new_entry

    def get_entries_by_date(self, user_id: int, target_date: date) -> List[MockJournalEntry]:
        """
        Recupera todas as entradas de diário para um utilizador numa data específica.
        """
        entries = [entry for entry in mock_journal_db 
                   if entry.user_id == user_id and entry.entry_date == target_date]
        
        print(f"A recuperar {len(entries)} entradas para o utilizador {user_id} em {target_date}.")
        return entries

    def search_entries(self, user_id: int, query: str) -> List[MockJournalEntry]:
        """
        Pesquisa entradas de diário por palavras-chave no conteúdo ou por tags.
        """
        search_results = []
        lower_query = query.lower()
        
        for entry in mock_journal_db:
            if entry.user_id != user_id:
                continue
            
            # Procura no conteúdo
            if lower_query in entry.content.lower():
                search_results.append(entry)
                continue
                
            # Procura nas tags
            if any(lower_query == tag.lower() for tag in entry.tags):
                search_results.append(entry)
                
        print(f"Pesquisa por '{query}' resultou em {len(search_results)} entradas.")
        
        # Remove duplicados caso a pesquisa encontre o mesmo item no conteúdo e nas tags
        unique_results = list({entry.id: entry for entry in search_results}.values())
        return unique_results

    def get_recent_entries(self, user_id: int, limit: int = 5) -> List[MockJournalEntry]:
        """
        Recupera as entradas de diário mais recentes do utilizador.
        """
        user_entries = [entry for entry in mock_journal_db if entry.user_id == user_id]
        # Ordena por data (mais recente primeiro)
        user_entries.sort(key=lambda x: x.entry_date, reverse=True)
        
        print(f"A recuperar as {limit} entradas mais recentes para o utilizador {user_id}.")
        return user_entries[:limit]