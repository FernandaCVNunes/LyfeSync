from datetime import date, timedelta
from typing import List, Dict, Any, Optional

# PLACEHOLDER: Usamos classes fictícias para simular os Modelos (MoodEntry)
class MockMoodEntry:
    def __init__(self, mood_level: int, notes: str, entry_date: date):
        self.mood_level = mood_level # 1 (Muito Mau) a 5 (Excelente)
        self.notes = notes
        self.entry_date = entry_date

class MoodService:
    """
    Encapsula a lógica de negócio para o registo, análise e correlação de humor (mood).
    Isto inclui calcular médias, identificar padrões e ligar o humor a hábitos/tarefas.
    """

    def __init__(self):
        pass

    def record_mood(self, user_id: int, mood_level: int, notes: str) -> MockMoodEntry:
        """
        Cria um novo registo de humor para o utilizador atual.
        Permite apenas um registo por dia (ou sobrescreve o existente).
        """
        if not 1 <= mood_level <= 5:
            raise ValueError("O nível de humor deve ser entre 1 e 5.")

        current_date = date.today()
        
        # Lógica real: Verifica se já existe uma entrada para hoje, se sim, atualiza;
        # caso contrário, cria uma nova.
        print(f"Registando humor ({mood_level}/5) para o utilizador {user_id} em {current_date}.")
        
        # Simulação
        new_entry = MockMoodEntry(mood_level, notes, current_date)
        return new_entry

    def get_mood_history(self, user_id: int, days: int = 30) -> List[MockMoodEntry]:
        """
        Recupera o histórico de registos de humor para o utilizador num determinado
        período (por defeito, 30 dias).
        """
        end_date = date.today()
        start_date = end_date - timedelta(days=days - 1)
        print(f"Buscando histórico de humor de {start_date} a {end_date} para o utilizador {user_id}.")

        # Simulação: Cria dados fictícios para os últimos 7 dias
        mock_history = [
            MockMoodEntry(4, "Dia produtivo, bom sono.", end_date - timedelta(days=0)),
            MockMoodEntry(3, "Um pouco stressado com o trabalho.", end_date - timedelta(days=1)),
            MockMoodEntry(5, "Fim de semana relaxante, fiz exercício.", end_date - timedelta(days=2)),
            MockMoodEntry(2, "Muito cansado e com pouca energia.", end_date - timedelta(days=3)),
        ]
        return mock_history

    def analyze_mood_average(self, user_id: int, days: int = 7) -> float:
        """
        Calcula o nível médio de humor do utilizador durante o período especificado.
        """
        history = self.get_mood_history(user_id, days=days)
        
        if not history:
            return 0.0

        total_sum = sum(entry.mood_level for entry in history)
        average = total_sum / len(history)

        print(f"Média de humor nos últimos {days} dias: {average:.2f}")
        
        return round(average, 2)

    def correlate_mood_with_habit(self, user_id: int, habit_id: int) -> Dict[str, Optional[float]]:
        """
        Analisa a correlação entre a conclusão de um hábito específico e o nível de humor
        no dia seguinte. Esta é uma funcionalidade analítica chave.
        """
        print(f"Analisando correlação entre Humor e Hábito ID {habit_id}...")
        
        # Lógica real (simplificada):
        # 1. Obter entradas de conclusão do hábito.
        # 2. Obter entradas de humor no dia imediatamente a seguir.
        # 3. Calcular a média de humor nos dias PÓS-conclusão vs. PÓS-falha.
        
        # Simulação:
        average_after_completion = 4.2
        average_after_failure = 3.1
        
        return {
            "average_after_completion": average_after_completion,
            "average_after_failure": average_after_failure
        }