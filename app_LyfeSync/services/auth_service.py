from typing import Optional, Dict, Any

# PLACEHOLDER: Usaremos um dicionário simples para simular um objeto de utilizador
# e a interação com a base de dados (o nosso futuro Modelo Django User).
class MockUser:
    """Classe fictícia para simular o modelo de utilizador do Django."""
    def __init__(self, user_id, username, email):
        self.id = user_id
        self.username = username
        self.email = email

class AuthService:
    """
    Encapsula toda a lógica de negócio relacionada com autenticação de utilizadores
    e gestão de perfis, interagindo diretamente com os Modelos Django (User).
    """

    def __init__(self):
        # Aqui podemos carregar configurações específicas de autenticação (e.g., JWT settings)
        pass

    def authenticate_user(self, username: str, password: str) -> Optional[MockUser]:
        """
        Tenta autenticar um utilizador com as credenciais fornecidas.

        Na implementação real, isto:
        1. Buscaria o utilizador pelo nome de utilizador.
        2. Verificaria se a password fornecida corresponde ao hash armazenado.
        """
        print(f"Tentativa de autenticação para: {username}")
        
        # Simulação: Sucesso se a password for 'test1234'
        if password == "test1234":
            print("Autenticação bem-sucedida.")
            # Lógica real: return User.objects.get(username=username)
            return MockUser(user_id=1, username=username, email=f"{username}@lyfesync.com")
        
        print("Autenticação falhada: credenciais inválidas.")
        return None

    def create_user(self, username: str, email: str, password: str) -> MockUser:
        """
        Regista um novo utilizador na aplicação.

        Na implementação real, isto:
        1. Validaria o nome de utilizador/email (unicidade).
        2. Criaria um novo objeto User com a password hasheada.
        """
        print(f"A criar novo utilizador: {username}, {email}")
        
        # Simulação: Cria e retorna um utilizador
        # Lógica real: User.objects.create_user(username, email, password)
        return MockUser(user_id=2, username=username, email=email)

    def get_user_profile(self, user_id: int) -> Optional[Dict[str, Any]]:
        """
        Obtém os dados do perfil de um utilizador, incluindo métricas básicas.
        """
        print(f"Buscando perfil para o utilizador ID: {user_id}")
        
        # Lógica real: Fetch User e dados relacionados (e.g., data de registo, contagem de hábitos)
        # Assumimos que o utilizador existe.
        return {
            "id": user_id,
            "username": "User" if user_id == 1 else "NovoUser",
            "email": f"user{user_id}@lyfesync.com",
            "date_joined": "2024-01-01",
            "metrics": {
                "total_habits": 5,
                "completion_rate_last_week": 0.85,
            }
        }

    def update_password(self, user_id: int, old_password: str, new_password: str) -> bool:
        """
        Muda a password de um utilizador após verificar a password antiga.
        """
        print(f"Tentativa de mudar password para o utilizador ID: {user_id}")
        
        # Simulação:
        if self.authenticate_user(username="test_user", password=old_password):
            # Lógica real: user.set_password(new_password) e user.save()
            print("Password atualizada com sucesso.")
            return True
        
        print("Falha ao atualizar a password: password antiga inválida.")
        return False