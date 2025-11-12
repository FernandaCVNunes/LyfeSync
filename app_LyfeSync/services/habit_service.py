from datetime import date, timedelta
from django.db.models import QuerySet

# Importamos os modelos necessários. Assumindo que Habit e HabitCompletion estão definidos
# noutro módulo, vamos usar uma importação relativa ou o caminho completo.
# Para este exemplo, vamos assumir que os modelos estão em app_LyfeSync.models
# (iremos criar esses modelos mais tarde).
# from app_LyfeSync.models import Habit, HabitCompletion

# PLACEHOLDER: Criamos classes fictícias para simular o comportamento dos modelos
# até que a estrutura de modelos seja implementada.
class MockHabit:
    def __init__(self, name, frequency):
        self.name = name
        self.frequency = frequency # Ex: 'daily', 'weekly'
class MockHabitCompletion:
    def __init__(self, habit, completion_date):
        self.habit = habit
        self.completion_date = completion_date

class HabitService:
    """
    Encapsula toda a lógica de negócio complexa relacionada com Hábitos.
    Isso inclui calcular 'streaks', verificar o estado de conclusão para um dia,
    e gerir o progresso geral.
    """

    def __init__(self):
        # Aqui, poderíamos inicializar caches ou outras dependências, se necessário.
        pass

    def get_user_habits(self, user_id: int) -> QuerySet:
        """
        Obtém todos os hábitos para um determinado utilizador.
        """
        # A lógica de serviço deve idealmente interagir com o ORM (Object-Relational Mapping)
        # para obter dados, mas sem conter a lógica de apresentação (views).
        print(f"Buscando hábitos para o utilizador {user_id}...")
        
        # Simulação: Retorna uma lista de objetos MockHabit
        mock_habits = [
            MockHabit("Beber 8 copos de água", "daily"),
            MockHabit("Ler 30 minutos", "daily"),
            MockHabit("Fazer exercício", "weekly")
        ]
        return mock_habits

    def check_completion(self, habit_id: int, completion_date: date = date.today()) -> bool:
        """
        Verifica se um hábito foi concluído na data especificada.
        """
        print(f"Verificando conclusão do hábito {habit_id} para {completion_date}...")
        # Lógica real: HabitCompletion.objects.filter(habit_id=habit_id, completion_date=completion_date).exists()
        
        # Simulação
        if habit_id == 1 and completion_date == date.today():
            return True # O hábito de Beber Água foi concluído hoje!
        return False

    def toggle_habit_completion(self, habit_id: int, user_id: int, completion_date: date = date.today()):
        """
        Marca um hábito como concluído ou desfeito para um determinado dia.
        """
        if self.check_completion(habit_id, completion_date):
            # Lógica real: Eliminar o registo de conclusão
            print(f"Removendo conclusão do hábito {habit_id} para {completion_date}.")
        else:
            # Lógica real: Criar um novo registo de conclusão
            print(f"Marcando hábito {habit_id} como concluído para {completion_date}.")
            
            # Simulação: Retorna um objeto MockHabitCompletion
            return MockHabitCompletion(MockHabit(f"Hábito {habit_id}", "daily"), completion_date)

    def calculate_streak(self, habit_id: int, user_id: int) -> int:
        """
        Calcula a 'streak' (sequência ininterrupta) atual de um hábito.
        Esta é uma lógica central e complexa de gestão de datas.
        """
        print(f"Calculando streak para o hábito {habit_id}...")
        
        # Lógica real envolvida:
        # 1. Obter todas as datas de conclusão para o hábito, ordenadas.
        # 2. Iterar sobre as datas, começando pelo dia anterior, verificando se cada dia
        #    consecutivo está na lista de conclusão.
        
        # Simulação (para demonstrar o conceito):
        if habit_id == 1:
            return 7 # Uma semana de streak!
        return 0


# Exemplo de como uma View utilizaria este serviço (isto NÃO é código da View):
"""
# Na View:
from .habit_service import HabitService
habit_svc = HabitService()
streak = habit_svc.calculate_streak(habit_id=1, user_id=1)
"""