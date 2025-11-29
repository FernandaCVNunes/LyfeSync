#test_funcionalidades
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from unittest.mock import patch, MagicMock
from datetime import date, timedelta

# Mock dos Modelos (Necessário para evitar erros ao renderizar templates que esperam dados)
class MockGratidao:
    objects = MagicMock()
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)

class MockHumor:
    objects = MagicMock()
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)
        
class MockHabito:
    objects = MagicMock()
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)
        self.dias_completos = {}
        
User = get_user_model()

# -------------------------------------------------------------------
# FUNÇÃO DE SETUP REUTILIZÁVEL
# -------------------------------------------------------------------
class BaseFunctionalTest(TestCase):
    """Classe base para configurar o cliente e o usuário de teste."""
    
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser', 
            email='test@example.com', 
            password='password123',
            is_staff=False # Usuário padrão
        )
        self.staff_user = User.objects.create_user(
            username='staffuser',
            email='staff@example.com',
            password='password123',
            is_staff=True # Usuário Staff para Dicas
        )
        
    def login(self, is_staff=False):
        """Faz o login com o usuário padrão ou staff."""
        user = self.staff_user if is_staff else self.user
        self.client.login(username=user.username, password='password123')
        return user

# -------------------------------------------------------------------
# 1. TESTES DE AUTENTICAÇÃO E PÁGINAS PÚBLICAS (Sem Login Necessário)
# -------------------------------------------------------------------
class PublicPagesTest(BaseFunctionalTest):

    # --- PÁGINAS PÚBLICAS GERAIS ---
    def test_home_page_render_success(self):
        """Testa o acesso e conteúdo da home pública."""
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'app_LyfeSync/public/home.html')
        self.assertContains(response, 'LyfeSync') # Verifica o nome da plataforma
        self.assertContains(response, f'href="{reverse("account_login")}"') # Verifica o link de login
        self.assertContains(response, 'masterpage.html') # Verifica o layout base

    def test_sobre_nos_page_render_success(self):
        """Testa o acesso e conteúdo da página Sobre Nós."""
        response = self.client.get(reverse('sobre_nos'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'app_LyfeSync/public/sobreNos.html')
        self.assertContains(response, 'Nossa Missão')

    def test_contatos_page_render_success(self):
        """Testa o acesso e conteúdo da página Contatos."""
        response = self.client.get(reverse('contatos'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'app_LyfeSync/public/contatos.html')
        self.assertContains(response, 'Entre em Contato')

    # --- TEMPLATES ALLAUTH (Autenticação) ---
    def test_login_page_render_success(self):
        """Testa a renderização do formulário de Login."""
        response = self.client.get(reverse('account_login'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'account/login.html')
        self.assertContains(response, 'Entrar')
        # Verifica a presença dos campos de form
        self.assertContains(response, 'type="password"') 

    def test_signup_page_render_success(self):
        """Testa a renderização do formulário de Cadastro (Sign Up)."""
        response = self.client.get(reverse('account_signup'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'account/signup.html')
        self.assertContains(response, 'Criar Conta')
        # CustomSignupForm deve incluir Nome e Sobrenome
        self.assertContains(response, 'Nome') 
        self.assertContains(response, 'Sobrenome')

    def test_logout_page_render_success(self):
        """Testa a renderização da página de Logout (GET)."""
        self.login()
        response = self.client.get(reverse('account_logout'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'account/logout.html')
        self.assertContains(response, 'Sair?')
        
    def test_login_social_cancelled_render_success(self):
        """Testa a renderização da página de Cancelamento de Login Social."""
        # A URL precisa ser configurada no seu allauth, mas aqui usamos o nome padrão
        response = self.client.get(reverse('socialaccount_login_cancelled'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'socialaccount/login_cancelled.html')
        self.assertContains(response, 'Cancelada')

# -------------------------------------------------------------------
# 2. TESTES DE ÁREA RESTRITA (Requer Login)
# -------------------------------------------------------------------
class RestrictedPagesTest(BaseFunctionalTest):
    
    def test_restricted_page_redirects_if_not_logged_in(self):
        """Testa se a página de Dashboard redireciona para login sem autenticação."""
        response = self.client.get(reverse('homeLyfesync'))
        # 302 é o código para redirecionamento
        self.assertEqual(response.status_code, 302) 
        # Verifica se redireciona para a página de login
        self.assertIn(reverse('account_login'), response.url) 

    # --- DASHBOARD E LAYOUT ---
    def test_homeLyfesync_render_success(self):
        """Testa o acesso e template do Dashboard."""
        self.login()
        response = self.client.get(reverse('homeLyfesync'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'app_LyfeSync/dashboard/homeLyfesync.html')
        self.assertContains(response, 'Seu Resumo Diário')
        self.assertContains(response, 'masterpage_logado.html') # Verifica o layout logado

    # --- CONTA ---
    def test_conta_page_render_success(self):
        """Testa a renderização da página de Conta."""
        self.login()
        response = self.client.get(reverse('conta'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'app_LyfeSync/conta/conta.html')
        self.assertContains(response, 'Configurações da Conta')
        # Verifica link para excluir conta
        self.assertContains(response, f'href="{reverse("excluir_conta")}"') 
        
    # --- AUTOCUIDADO (Página Mestra) ---
    def test_autocuidado_page_render_success(self):
        """Testa a renderização da página Mestra de Autocuidado."""
        self.login()
        response = self.client.get(reverse('autocuidado'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'app_LyfeSync/autocuidado/autocuidado.html')
        self.assertContains(response, 'Menu de Autocuidado')
        # Verifica link para Gratidão
        self.assertContains(response, f'href="{reverse("gratidao")}"') 

# -------------------------------------------------------------------
# 3. TESTES DE MÓDULOS (HABITO, GRATIDÃO, HUMOR, AFIRMAÇÃO)
# -------------------------------------------------------------------
class ModulosAutocuidadoTest(BaseFunctionalTest):
    
    def setUp(self):
        super().setUp()
        self.user_logged = self.login()
        
        # Cria um objeto mockado (se necessário) para renderizar dados
        self.gratidao_mock = MockGratidao(descricaogratidao='Grato por teste')
        self.habito_mock = MockHabito(nome='Beber Água', frequencia='D', id=1, pk=1)

    # --- HÁBITO ---
    @patch('app_LyfeSync.views.Habito.objects.filter')
    def test_habito_page_render_success(self, mock_filter):
        """Testa a página de Hábitos e a listagem de dados (simulada)."""
        mock_filter.return_value = [self.habito_mock]
        
        response = self.client.get(reverse('habito'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'app_LyfeSync/habitos/habito.html')
        self.assertContains(response, 'Meus Hábitos')
        self.assertContains(response, 'Beber Água') # Verifica listagem do mock
        
    @patch('app_LyfeSync.views.Habito.objects.get')
    def test_alterar_habito_page_render_success(self, mock_get):
        """Testa a renderização do formulário de alteração de Hábito."""
        mock_get.return_value = self.habito_mock
        
        response = self.client.get(reverse('alterar_habito', args=[1]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'app_LyfeSync/habitos/alterarHabito.html')
        self.assertContains(response, 'Alterar Hábito')
        self.assertContains(response, 'value="Beber Água"') # Verifica nome pré-preenchido

    # --- GRATIDÃO ---
    @patch('app_LyfeSync.views.Gratidao.objects.filter')
    def test_gratidao_page_render_success(self, mock_filter):
        """Testa a página de Gratidão e a listagem de dados (simulada)."""
        mock_filter.return_value = [self.gratidao_mock]
        
        response = self.client.get(reverse('gratidao'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'app_LyfeSync/autocuidado/gratidao.html')
        self.assertContains(response, 'Diário de Gratidão')
        self.assertContains(response, 'Grato por teste') # Verifica listagem do mock

    # --- HUMOR ---
    @patch('app_LyfeSync.views.Humor.objects.filter')
    def test_humor_page_render_success(self, mock_filter):
        """Testa a página de Humor e a listagem (simulada)."""
        # Mock do filtro que a view usa para buscar o humor do mês
        mock_filter.return_value = [MockHumor(estado='Feliz', data=date.today())] 
        
        response = self.client.get(reverse('humor'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'app_LyfeSync/autocuidado/humor.html')
        self.assertContains(response, 'Rastreador de Humor')
        self.assertContains(response, 'Feliz') 
        # Verifica se o formulário de registro está presente
        self.assertContains(response, 'name="estado"')

    # --- AFIRMAÇÃO ---
    @patch('app_LyfeSync.views.Afirmacao.objects.filter')
    def test_afirmacao_page_render_success(self, mock_filter):
        """Testa a página de Afirmação e a listagem (simulada)."""
        mock_filter.return_value = [MagicMock(descricaogratidao='Eu sou forte')]
        
        response = self.client.get(reverse('afirmacao'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'app_LyfeSync/autocuidado/afirmacao.html')
        self.assertContains(response, 'Afirmações Positivas')
        self.assertContains(response, 'Eu sou forte')
        # Verifica a presença do campo de descrição do form
        self.assertContains(response, 'name="descricao_1"') 

    # --- DICAS (Acesso restrito ao Staff) ---
    def test_dicas_registrar_render_staff_success(self):
        """Testa o acesso à página de registro de Dicas por um usuário Staff."""
        self.login(is_staff=True)
        response = self.client.get(reverse('registrar_dica'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'app_LyfeSync/autocuidado/dicas.html')
        self.assertContains(response, 'Cadastrar Nova Dica')

    def test_dicas_registrar_denied_for_regular_user(self):
        """Testa o acesso à página de registro de Dicas por um usuário comum."""
        self.login()
        response = self.client.get(reverse('registrar_dica'))
        # Deve retornar 403 Forbidden (ou 302 se redirecionar para um erro)
        self.assertEqual(response.status_code, 403) 

# -------------------------------------------------------------------
# 4. TESTES DE RELATÓRIOS
# -------------------------------------------------------------------
class RelatoriosTest(BaseFunctionalTest):
    
    def setUp(self):
        super().setUp()
        self.login()

    def test_relatorios_page_render_success(self):
        """Testa a página Mestra de Relatórios."""
        response = self.client.get(reverse('relatorios'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'app_LyfeSync/relatórios/relatorios.html')
        self.assertContains(response, 'Dashboard de Relatórios')
        self.assertContains(response, f'href="{reverse("relatorio_habito")}"') # Verifica link para Sub-relatório

    def test_relatorio_habito_page_render_success(self):
        """Testa a página de Relatório de Hábitos."""
        response = self.client.get(reverse('relatorio_habito'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'app_LyfeSync/relatórios/relatorioHabito.html')
        self.assertContains(response, 'Relatório de Conclusão de Hábitos')
        
    def test_relatorio_humor_page_render_success(self):
        """Testa a página de Relatório de Humor."""
        response = self.client.get(reverse('relatorio_humor'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'app_LyfeSync/relatórios/relatorioHumor.html')
        self.assertContains(response, 'Distribuição Mensal de Humor')
        # Verifica a presença do formulário de seleção de Mês/Ano
        self.assertContains(response, 'name="mes"') 
        
    def test_relatorio_gratidao_page_render_success(self):
        """Testa a página de Relatório de Gratidão."""
        response = self.client.get(reverse('relatorio_gratidao'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'app_LyfeSync/relatórios/relatorioGratidao.html')
        self.assertContains(response, 'Análise de Sentimentos em Gratidão')
        
    def test_relatorio_afirmacao_page_render_success(self):
        """Testa a página de Relatório de Afirmação."""
        response = self.client.get(reverse('relatorio_afirmacao'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'app_LyfeSync/relatórios/relatórioAfirmacao.html')
        self.assertContains(response, 'Análise de Frequência de Afirmações')
    
# -------------------------------------------------------------------
# 5. TESTES DE FLUXO E SUBMISSÃO (POST)
# -------------------------------------------------------------------

class FunctionalFlowTest(BaseFunctionalTest):
    
    def setUp(self):
        super().setUp()
        self.user_logged = self.login()
        self.today = date.today().strftime('%Y-%m-%d')
        
    # --- HABITOS: REGISTRAR ---
    @patch('app_LyfeSync.views.HabitoForm')
    def test_registrar_habito_post_success(self, MockHabitoForm):
        """Testa a submissão bem-sucedida do formulário de registro de hábito."""
        # 1. Configura o mock do formulário e o método save
        mock_form_instance = MockHabitoForm.return_value
        mock_form_instance.is_valid.return_value = True
        
        # 2. Dados de submissão
        post_data = {
            'nome': 'Novo Hábito',
            'data_inicio': self.today,
            'frequencia': 'D',
            # Outros campos são opcionais ou têm valor padrão
        }
        
        # 3. Executa a requisição POST
        response = self.client.post(reverse('registrar_habito'), data=post_data, follow=True)
        
        # 4. Asserções
        # Verifica se o save foi chamado
        mock_form_instance.save.assert_called_once()
        # Verifica se houve redirecionamento de sucesso (para a página de hábitos)
        self.assertEqual(response.status_code, 200) 
        self.assertTemplateUsed(response, 'app_LyfeSync/habitos/habito.html') 
        self.assertContains(response, 'Hábito cadastrado com sucesso!') # Assumindo que a view envia uma mensagem

    # --- GRATIDÃO: REGISTRAR (com save customizado) ---
    @patch('app_LyfeSync.views.GratidaoCreateForm')
    def test_registrar_gratidao_post_success(self, MockGratidaoCreateForm):
        """Testa a submissão bem-sucedida do formulário de registro de gratidão (múltiplos)."""
        # 1. Configura o mock do formulário e o método save
        mock_form_instance = MockGratidaoCreateForm.return_value
        mock_form_instance.is_valid.return_value = True
        mock_form_instance.save.return_value = [MagicMock(), MagicMock()] # Simula a criação de 2 objetos
        
        # 2. Dados de submissão
        post_data = {
            'data': self.today,
            'descricaogratidao_1': 'Grato pelo sol',
            'descricaogratidao_2': 'Grato pela água',
        }
        
        # 3. Executa a requisição POST
        response = self.client.post(reverse('registrar_gratidao'), data=post_data, follow=True)
        
        # 4. Asserções
        # Verifica se o save customizado foi chamado
        mock_form_instance.save.assert_called_once_with(user=self.user_logged)
        # Verifica se houve redirecionamento de sucesso (para a página de gratidão)
        self.assertEqual(response.status_code, 200) 
        self.assertTemplateUsed(response, 'app_LyfeSync/autocuidado/gratidao.html') 
        self.assertContains(response, 'Gratidão registrada com sucesso!')

    # --- HUMOR: REGISTRAR ---
    @patch('app_LyfeSync.views.HumorForm')
    def test_registrar_humor_post_success(self, MockHumorForm):
        """Testa o registro de humor."""
        # 1. Configura o mock do formulário
        mock_form_instance = MockHumorForm.return_value
        mock_form_instance.is_valid.return_value = True
        mock_humor_saved = MagicMock(pk=1)
        mock_form_instance.save.return_value = mock_humor_saved
        
        # 2. Dados de submissão
        post_data = {'estado': 1, 'descricaohumor': 'Me sentindo ótimo', 'data': self.today}
        
        # 3. Executa a requisição POST
        response = self.client.post(reverse('registrarHumor'), data=post_data, follow=True)
        
        # 4. Asserções
        mock_form_instance.save.assert_called_once()
        # Redireciona para 'humor' após o sucesso
        self.assertEqual(response.status_code, 200) 
        self.assertTemplateUsed(response, 'app_LyfeSync/autocuidado/humor.html') 
        self.assertContains(response, 'Humor registrado com sucesso!')

    # --- AFIRMAÇÃO: REGISTRAR ---
    @patch('app_LyfeSync.views.AfirmacaoRegistroForm')
    @patch('app_LyfeSync.views.Afirmacao.objects.bulk_create') # Assumindo bulk_create na view
    def test_registrar_afirmacao_post_success(self, mock_bulk_create, MockAfirmacaoRegistroForm):
        """Testa o registro de múltiplas afirmações."""
        # 1. Configura o mock do formulário
        mock_form_instance = MockAfirmacaoRegistroForm.return_value
        mock_form_instance.is_valid.return_value = True
        mock_form_instance.cleaned_data = {
            'data': date.today(),
            'descricao_1': 'Sou forte',
            'descricao_2': 'Sou feliz',
            'descricao_3': ''
        }
        
        # 2. Dados de submissão
        post_data = {'data': self.today, 'descricao_1': 'Sou forte'}
        
        # 3. Executa a requisição POST
        response = self.client.post(reverse('registrar_afirmacao'), data=post_data, follow=True)
        
        # 4. Asserções
        self.assertTrue(mock_bulk_create.called) # Deve chamar a criação em lote
        # Redireciona para 'afirmacao'
        self.assertEqual(response.status_code, 200) 
        self.assertTemplateUsed(response, 'app_LyfeSync/autocuidado/afirmacao.html') 
        self.assertContains(response, 'Afirmações registradas com sucesso!')


    # --- DICAS: REGISTRAR (Flow Staff) ---
    @patch('app_LyfeSync.views.DicasForm')
    def test_registrar_dica_post_success_staff(self, MockDicasForm):
        """Testa a submissão bem-sucedida do formulário de dicas por Staff."""
        self.staff_logged = self.login(is_staff=True)
        
        # 1. Configura o mock do formulário
        mock_form_instance = MockDicasForm.return_value
        mock_form_instance.is_valid.return_value = True
        mock_dica_saved = MagicMock(pk=1)
        mock_form_instance.save.return_value = mock_dica_saved
        
        # 2. Dados de submissão
        post_data = {'nomeDica': 'Respirar', 'descricaoDica': '4-7-8', 'humor_relacionado': 1, 'criado_por': self.staff_logged.pk}
        
        # 3. Executa a requisição POST
        response = self.client.post(reverse('registrar_dica'), data=post_data, follow=True)
        
        # 4. Asserções
        # Verifica se o save foi chamado
        self.assertTrue(mock_form_instance.save.called) 
        # Verifica se houve redirecionamento de sucesso (assumindo que redireciona para a lista de dicas ou autocuidado)
        # Assumindo que redireciona para 'autocuidado'
        self.assertEqual(response.status_code, 200) 
        self.assertTemplateUsed(response, 'app_LyfeSync/autocuidado/autocuidado.html') 
        self.assertContains(response, 'Dica registrada com sucesso!')
        
    def test_registrar_dica_post_denied_regular_user(self):
        """Testa se usuário comum é impedido de registrar dica (403)."""
        # Dados de submissão
        post_data = {'nomeDica': 'Respirar', 'descricaoDica': '4-7-8', 'humor_relacionado': 1}
        # 3. Executa a requisição POST
        response = self.client.post(reverse('registrar_dica'), data=post_data)
        
        # 4. Asserções
        self.assertEqual(response.status_code, 403) # Deve retornar Proibido

    
class FunctionalOperationTest(BaseFunctionalTest):
    
    def setUp(self):
        super().setUp()
        self.user_logged = self.login()
        
        # Mocks para objetos que serão manipulados/deletados
        self.mock_habito = MagicMock(pk=99, usuario=self.user_logged)
        self.mock_humor = MagicMock(pk=98, usuario=self.user_logged)
        self.mock_gratidao = MagicMock(pk=97, usuario=self.user_logged)
        self.mock_afirmacao = MagicMock(pk=96, usuario=self.user_logged)

    # --- HÁBITOS ---
    @patch('app_LyfeSync.views.Habito.objects.get')
    def test_delete_habit_post_success(self, mock_get):
        """Testa a exclusão de um hábito e o redirecionamento."""
        mock_get.return_value = self.mock_habito
        self.mock_habito.delete = MagicMock() # Mocka o método de exclusão
        
        url = reverse('delete_habit', args=[self.mock_habito.pk])
        response = self.client.post(url, follow=True) 
        
        # 1. Verifica se o método de exclusão foi chamado
        self.mock_habito.delete.assert_called_once()
        
        # 2. Verifica o redirecionamento para a página de hábitos (200 OK após follow)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'app_LyfeSync/habitos/habito.html')
        self.assertContains(response, 'Hábito excluído com sucesso!') 
        
    @patch('app_LyfeSync.views.Habito.objects.get')
    def test_toggle_habit_day_success(self, mock_get):
        """Testa a rota AJAX para marcar/desmarcar um dia de hábito."""
        mock_get.return_value = self.mock_habito
        # Mocka a função da view que gerencia o toggle
        with patch('app_LyfeSync.views.toggle_habito_day_logic', return_value={'success': True, 'completed': True}) as mock_toggle:
            
            url = reverse('toggle_habit_day', args=[self.mock_habito.pk, 'segunda'])
            response = self.client.post(url, data={'is_ajax': True})
            
            # 1. Deve retornar 200 (sucesso da requisição AJAX)
            self.assertEqual(response.status_code, 200)
            
            # 2. O conteúdo deve ser JSON
            self.assertEqual(response['Content-Type'], 'application/json')
            
            # 3. Verifica o conteúdo JSON
            self.assertContains(response, 'true', status_code=200) 
            mock_toggle.assert_called_once()


    # --- HUMOR ---
    @patch('app_LyfeSync.views.Humor.objects.get')
    def test_delete_humor_success(self, mock_get):
        """Testa a exclusão de um registro de humor."""
        mock_get.return_value = self.mock_humor
        self.mock_humor.delete = MagicMock()
        
        url = reverse('deleteHumor', args=[self.mock_humor.pk])
        response = self.client.post(url, follow=True)
        
        self.mock_humor.delete.assert_called_once()
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'app_LyfeSync/autocuidado/humor.html') 
        self.assertContains(response, 'Registro de humor excluído com sucesso!')
        
    # --- GRATIDÃO ---
    @patch('app_LyfeSync.views.Gratidao.objects.get')
    def test_delete_gratidao_success(self, mock_get):
        """Testa a exclusão de um registro de gratidão."""
        mock_get.return_value = self.mock_gratidao
        self.mock_gratidao.delete = MagicMock()
        
        url = reverse('delete_gratidao', args=[self.mock_gratidao.pk])
        response = self.client.post(url, follow=True)
        
        self.mock_gratidao.delete.assert_called_once()
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'app_LyfeSync/autocuidado/gratidao.html') 
        self.assertContains(response, 'Registro de gratidão excluído com sucesso!')

    # --- AFIRMAÇÃO ---
    @patch('app_LyfeSync.views.Afirmacao.objects.get')
    def test_delete_afirmacao_success(self, mock_get):
        """Testa a exclusão de um registro de afirmação."""
        mock_get.return_value = self.mock_afirmacao
        self.mock_afirmacao.delete = MagicMock()
        
        url = reverse('delete_afirmacao', args=[self.mock_afirmacao.pk])
        response = self.client.post(url, follow=True)
        
        self.mock_afirmacao.delete.assert_called_once()
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'app_LyfeSync/autocuidado/afirmacao.html') 
        self.assertContains(response, 'Afirmação excluída com sucesso!')


class FunctionalAuthorizationTest(BaseFunctionalTest):
    
    def setUp(self):
        super().setUp()
        # User A está logado (o atacante)
        self.user_a = self.login() 
        # User B (o alvo)
        self.user_b = User.objects.create_user(username='usertarget', email='target@example.com', password='password123')
        
        # Mock do Hábito pertencente ao User B
        self.habito_b = MagicMock(pk=100, usuario=self.user_b) 
        self.habito_b.delete = MagicMock()

    @patch('app_LyfeSync.views.Habito.objects.get')
    def test_delete_habit_of_other_user_denied(self, mock_get):
        """Testa se o User A é impedido de excluir o hábito do User B."""
        mock_get.return_value = self.habito_b 
        
        url = reverse('delete_habit', args=[self.habito_b.pk])
        response = self.client.post(url)
        
        # 1. O delete NÃO deve ser chamado
        self.habito_b.delete.assert_not_called()
        
        # 2. Verifica se retorna 403 (Forbidden) ou 404 (Not Found, que é mais seguro)
        self.assertIn(response.status_code, [403, 404])
        
    @patch('app_LyfeSync.views.Gratidao.objects.get')
    def test_alterar_gratidao_of_other_user_denied(self, mock_get):
        """Testa se o User A é impedido de renderizar a página de alteração do Gratidão do User B."""
        mock_gratidao_b = MagicMock(pk=200, usuario=self.user_b)
        mock_get.return_value = mock_gratidao_b
        
        url = reverse('alterar_gratidao', args=[mock_gratidao_b.pk])
        response = self.client.get(url)
        
        # Deve retornar erro de permissão/não encontrado
        self.assertIn(response.status_code, [403, 404])

class FunctionalExportTest(BaseFunctionalTest):
    
    def setUp(self):
        super().setUp()
        self.user_logged = self.login()
        
    # --- EXPORTAÇÃO CSV ---
    @patch('app_LyfeSync.views.Habito.objects.filter')
    def test_exportar_habito_csv_success(self, mock_filter):
        """Testa a exportação de CSV de hábitos (tipo de conteúdo e dados)."""
        # Mock dos dados que serão exportados
        mock_filter.return_value = [
            MagicMock(nome='Ler Livro', data_inicio=date(2025, 1, 1), frequencia='D'),
        ]
        
        response = self.client.get(reverse('exportar_habito_csv'))
        
        # 1. Verifica o status code
        self.assertEqual(response.status_code, 200)
        
        # 2. Verifica o cabeçalho do conteúdo (MIME type para CSV)
        self.assertEqual(response['Content-Type'], 'text/csv')
        
        # 3. Verifica o cabeçalho de download
        self.assertIn('attachment; filename="relatorio_habitos_', response['Content-Disposition'])
        
        # 4. Verifica se o conteúdo do CSV (mockado) está presente
        content = response.content.decode('utf-8')
        self.assertIn('Ler Livro', content)
        self.assertIn('2025-01-01', content)

    # --- EXPORTAÇÃO PDF ---
    # *AVISO: Mockar a geração de PDF (como reportlab ou weasyprint) é complexo. 
    # Aqui, testamos apenas o cabeçalho e o status, assumindo que a biblioteca está funcionando.*
    @patch('app_LyfeSync.views.gerar_pdf_habito') # Mocka a função que realmente gera o PDF
    def test_exportar_habito_pdf_success(self, mock_gerar_pdf):
        """Testa a exportação de PDF de hábitos (tipo de conteúdo)."""
        # Simula um conteúdo PDF binário
        mock_gerar_pdf.return_value = MagicMock(content=b'%PDF-1.4...', status_code=200, 
                                                get=lambda x: 'application/pdf') 
        
        response = self.client.get(reverse('exportar_habito_pdf'))
        
        # 1. Verifica o status code
        self.assertEqual(response.status_code, 200)
        
        # 2. Verifica o cabeçalho do conteúdo (MIME type para PDF)
        self.assertEqual(response['Content-Type'], 'application/pdf')
        
        # 3. Verifica o cabeçalho de download
        self.assertIn('attachment; filename="relatorio_habitos_', response['Content-Disposition'])

