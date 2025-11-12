from datetime import date, timedelta
from typing import List, Dict, Any, Optional

# PLACEHOLDER: Usamos classes fictícias para simular o Modelo (Task)
class MockTask:
    """Classe fictícia para simular o modelo de Tarefa (Task) do Django."""
    def __init__(self, task_id: int, user_id: int, title: str, due_date: date, is_completed: bool = False):
        self.id = task_id
        self.user_id = user_id
        self.title = title
        self.due_date = due_date
        self.is_completed = is_completed

# Dicionário fictício para simular a base de dados de tarefas
mock_tasks_db: List[MockTask] = [
    MockTask(1, 1, "Pagar a conta da eletricidade", date.today(), False),
    MockTask(2, 1, "Enviar e-mail de acompanhamento", date.today(), True),
    MockTask(3, 1, "Comprar prendas de aniversário", date.today() + timedelta(days=2), False),
    MockTask(4, 1, "Rever o relatório mensal", date.today() - timedelta(days=1), False), # Tarefa em atraso
    MockTask(5, 2, "Reunião de equipa", date.today(), False),
]

class TaskService:
    """
    Encapsula a lógica de negócio para a criação, gestão, e conclusão de tarefas (To-Do).
    """

    def __init__(self):
        self.next_id = len(mock_tasks_db) + 1
        pass

    def create_task(self, user_id: int, title: str, due_date: date) -> MockTask:
        """
        Adiciona uma nova tarefa à lista de afazeres.
        """
        print(f"A criar nova tarefa para o utilizador {user_id}: '{title}' com data limite {due_date}.")
        
        # Lógica real: Task.objects.create(...)
        new_task = MockTask(self.next_id, user_id, title, due_date)
        mock_tasks_db.append(new_task)
        self.next_id += 1
        return new_task

    def get_tasks(self, user_id: int, include_completed: bool = False, date_filter: Optional[date] = None) -> List[MockTask]:
        """
        Recupera as tarefas de um utilizador, com opções para filtrar por data e estado.
        """
        filtered_tasks = [task for task in mock_tasks_db if task.user_id == user_id]

        if not include_completed:
            filtered_tasks = [task for task in filtered_tasks if not task.is_completed]
        
        if date_filter:
            filtered_tasks = [task for task in filtered_tasks if task.due_date == date_filter]
        
        print(f"A recuperar {len(filtered_tasks)} tarefas para o utilizador {user_id}.")
        return filtered_tasks

    def complete_task(self, user_id: int, task_id: int) -> Optional[MockTask]:
        """
        Marca uma tarefa específica como concluída.
        """
        # Lógica real: Tenta obter a tarefa e atualizar o campo is_completed
        task_to_update = next((task for task in mock_tasks_db if task.id == task_id and task.user_id == user_id), None)

        if task_to_update:
            task_to_update.is_completed = True
            print(f"Tarefa ID {task_id} marcada como concluída.")
            return task_to_update
        
        print(f"Erro: Tarefa ID {task_id} não encontrada ou não pertence ao utilizador {user_id}.")
        return None

    def get_daily_stats(self, user_id: int, target_date: date) -> Dict[str, Any]:
        """
        Calcula as estatísticas de conclusão de tarefas para um dia específico.
        """
        daily_tasks = [task for task in mock_tasks_db 
                       if task.user_id == user_id and task.due_date == target_date]

        total_tasks = len(daily_tasks)
        completed_tasks = sum(1 for task in daily_tasks if task.is_completed)
        
        completion_rate = (completed_tasks / total_tasks) * 100 if total_tasks > 0 else 0
        
        print(f"Estatísticas de tarefas para {target_date}: {completed_tasks}/{total_tasks} concluídas.")

        return {
            "total_tasks": total_tasks,
            "completed_tasks": completed_tasks,
            "completion_rate": round(completion_rate, 2),
        }