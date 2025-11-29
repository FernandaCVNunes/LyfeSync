# test_views.py
import csv
from datetime import date, timedelta
from io import BytesIO
from unittest import TestCase, mock
from unittest.mock import MagicMock, patch, call, Mock
from django.contrib.messages import get_messages
from django.test import RequestFactory, override_settings
from django.urls import reverse
from django.conf import settings
from django.http import Http404, JsonResponse

# Configurações mínimas do Django para que o RequestFactory funcione
# O arquivo de teste real deve estar no ambiente do projeto, mas esta é a simulação.
settings.configure(
    SECRET_KEY='fake-key',
    TEMPLATES=[{
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
    }],
    MIDDLEWARE=[
        'django.contrib.sessions.middleware.SessionMiddleware',
        'django.contrib.messages.middleware.MessageMiddleware',
        'django.contrib.auth.middleware.AuthenticationMiddleware',
    ],
    # Adicionando settings para URL reverse
    ROOT_URLCONF='tests.urls', 
    INSTALLED_APPS=[
        'django.contrib.auth',
        'django.contrib.contenttypes',
        'django.contrib.sessions',
        'django.contrib.messages',
        'app_LyfeSync', # Substitua pelo nome do seu app real
    ],
)

# Simulando um arquivo urls.py mínimo necessário para os reverses
class MockUrls:
    def __init__(self):
        # Mapeamento de nomes de URL para simular as URLs que as views usam
        self.url_map = {
            'login': '/login/',
            'relatorios': '/relatorios/',
            'relatorio_humor': '/humor/relatorio/',
            'humor': '/humor/',
            'gratidao': '/gratidao/',
            'afirmacao': '/afirmacao/',
            'registrar_dica': '/dicas/registrar/',
        }
    def reverse(self, viewname, args=None, kwargs=None):
        return self.url_map.get(viewname, f'/{viewname}/')

# Força o reverse a usar a nossa classe mock
# Isso é necessário para rodar o código fora do ambiente Django completo
reverse = MockUrls().reverse


# --- MOCKS DE MODELS E INSTÂNCIAS AUXILIARES ---

class MockHumorTipo:
    def __init__(self, pk, estado, icone='path/icone.svg'):
        self.pk = pk
        self.id_tipo_humor = pk
        self.estado = estado
        self.icone = icone
    def __str__(self): return self.estado

class MockHumor:
    def __init__(self, pk, user, data, estado, descricaohumor=''):
        self.pk = pk
        self.idhumor = pk
        self.usuario = user
        self.data = data
        self.estado = estado
        self.descricaohumor = descricaohumor
    def save(self, *args, **kwargs): pass
    def delete(self, *args, **kwargs): pass
    
class MockDicas:
    def __init__(self, pk, nomeDica, descricaodica, humor_relacionado, data_criacao=date.today(), criado_por=None):
        self.pk = pk
        self.id_dicas = pk
        self.nomeDica = nomeDica
        self.descricaodica = descricaodica
        self.humor_relacionado = humor_relacionado
        self.data_criacao = data_criacao
        self.criado_por = criado_por
    def __str__(self): return self.nomeDica
    def delete(self, *args, **kwargs): pass

class MockGratidao:
    def __init__(self, pk, user, data, descricaogratidao, data_registro=None):
        self.pk = pk
        self.idgratidao = pk
        self.usuario = user
        self.data = data
        self.descricaogratidao = descricaogratidao
        self.data_registro = data_registro or date.today()
    def delete(self, *args, **kwargs): pass
    def save(self, *args, **kwargs): pass

class MockAfirmacao:
    def __init__(self, pk, user, data, descricaoafirmacao, data_registro=None):
        self.pk = pk
        self.idafirmacao = pk
        self.usuario = user
        self.data = data
        self.descricaoafirmacao = descricaoafirmacao
        self.data_registro = data_registro or date.today()
    def delete(self, *args, **kwargs): pass
    def save(self, *args, **kwargs): pass

class MockHabito:
    def __init__(self, pk, user, nome, data_inicio, data_fim=None):
        self.pk = pk
        self.id = pk
        self.usuario = user
        self.nome = nome
        self.data_inicio = data_inicio
        self.data_fim = data_fim
    def __str__(self): return self.nome

class MockStatusDiario:
    def __init__(self, pk, habito, data, concluido):
        self.pk = pk
        self.habito = habito
        self.data = data
        self.concluido = concluido
        self.habito_id = habito.pk
    def __str__(self): return f'{self.habito.nome} - {self.data}'


# Usuário Mock Padrão
class MockUser:
    def __init__(self, pk=1, username='testuser', is_staff=False, is_active=True):
        self.pk = pk
        self.username = username
        self.is_staff = is_staff
        self.is_active = is_active
        self.is_authenticated = True
    def __str__(self): return self.username

mock_user = MockUser()
mock_staff_user = MockUser(pk=2, username='staffuser', is_staff=True)

# Instâncias de HumorTipo para uso geral
TIPO_FELIZ = MockHumorTipo(pk=1, estado='Feliz', icone='feliz.svg')
TIPO_TRISTE = MockHumorTipo(pk=2, estado='Triste', icone='triste.svg')


# --- CLASSE BASE DE TESTE COM SETUP ---

@override_settings(ROOT_URLCONF='tests.urls')
class BaseViewTest(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = mock_user
        self.staff_user = mock_staff_user
        self.hoje = date.today()

    def _get_messages(self, response):
        return [str(m) for m in get_messages(response.wsgi_request)]

    def _get_request(self, method, url, user=None, data=None, session=None):
        if method == 'GET':
            request = self.factory.get(url, data=data)
        elif method == 'POST':
            request = self.factory.post(url, data=data)
        else:
            raise ValueError("Método HTTP não suportado")
        
        request.user = user or self.user
        request.session = session or self.client.session
        request.method = method
        
        # Simula o wsgi_request necessário para o get_messages e outras funções
        request._dont_enforce_csrf_checks = True # Desativa a verificação CSRF para POST
        
        return request

    def _simulate_login_required(self, view_func, url):
        # Testa redirecionamento de usuário não autenticado
        request = self._get_request('GET', url, user=Mock(is_authenticated=False))
        response = view_func(request)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url.startswith('/login/'))

# --- MOCKS GLOBAIS DE FUNÇÕES E CLASSES ---

# Mock das Funções Auxiliares (reports_views)
MOCK_REPORT_FUNCTIONS = {
    '_get_report_date_range': MagicMock(return_value=(
        date(2024, 1, 1), # data_inicio
        date(2024, 1, 31), # data_fim
        date(2024, 1, 1), # data_referencia
        'mensal', # periodo
        1, # mes_param
        2024 # ano_param
    )),
    'get_habitos_e_acompanhamento': MagicMock(return_value=[
        {'id': 1, 'nome': 'Habito A', 'acompanhamento': {date(2024, 1, 1): True, date(2024, 1, 2): False}},
    ]),
    'convert_html_to_pdf': MagicMock(side_effect=lambda html, filename, request: Mock(status_code=200, content=b'PDF_Content', content_type='application/pdf')),
    'get_humor_map': MagicMock(return_value={}),
    '_get_humor_cor_classe': MagicMock(return_value='#123456'),
    'get_humor_icone': MagicMock(return_value='path/icon.svg'),
}

# Mock das Funções Auxiliares (selfcare_views)
MOCK_SELFCARE_FUNCTIONS = {
    'extract_dica_info': MagicMock(side_effect=lambda desc: (10 if '[DICA ID:10]' in desc else None, desc.replace('[DICA ID:10]', '').strip())),
    'rebuild_descricaohumor': MagicMock(side_effect=lambda dica_id, desc: f'[DICA ID:{dica_id}] {desc}' if dica_id else desc),
}

# Mock dos Forms (apenas para simular a validação)
MockForm = lambda name: MagicMock(name=name, is_valid=lambda: True, cleaned_data={'campo': 'valor'}, save=lambda *args, **kwargs: Mock(pk=1))
MOCK_FORMS = {
    'HumorForm': MockForm('HumorForm'),
    'DicasForm': MockForm('DicasForm'),
    'RelatorioHumorForm': MockForm('RelatorioHumorForm'),
    'RelatorioHabitoForm': MagicMock(is_valid=lambda: True, cleaned_data={'mes': 1, 'ano': 2024}),
    'GratidaoCreateForm': MagicMock(
        is_valid=lambda: True, 
        cleaned_data={'data': date.today(), 'descricao_1': 'g1'},
        save=lambda *args, **kwargs: [MockGratidao(1, mock_user, date.today(), 'g1')]
    ),
    'GratidaoUpdateForm': MagicMock(
        is_valid=lambda: True, 
        cleaned_data={'descricaogratidao': 'Nova Gratidão Alterada'}
    ),
    'AfirmacaoRegistroForm': MagicMock(
        is_valid=lambda: True,
        cleaned_data={
            'data': date.today(),
            'descricao_1': 'Afirmação 1',
            'descricao_2': 'Afirmação 2',
            'descricao_3': ''
        }
    ),
    'AfirmacaoAlteracaoForm': MagicMock(
        is_valid=lambda: True,
        cleaned_data={'descricaoafirmacao': 'Afirmação Alterada'}
    ),
}

# --- TESTES PARA app_LyfeSync/views/selfcare_views.py ---

@patch.dict('app_LyfeSync.views.selfcare_views.__builtins__', {'HumorForm': MOCK_FORMS['HumorForm'], 'DicasForm': MOCK_FORMS['DicasForm'], 'GratidaoCreateForm': MOCK_FORMS['GratidaoCreateForm'], 'GratidaoUpdateForm': MOCK_FORMS['GratidaoUpdateForm'], 'AfirmacaoRegistroForm': MOCK_FORMS['AfirmacaoRegistroForm'], 'AfirmacaoAlteracaoForm': MOCK_FORMS['AfirmacaoAlteracaoForm']}, clear=False)
@patch.dict('app_LyfeSync.views.selfcare_views.__builtins__', MOCK_SELFCARE_FUNCTIONS, clear=False)
@patch('app_LyfeSync.views.selfcare_views.Afirmacao', autospec=True)
@patch('app_LyfeSync.views.selfcare_views.Gratidao', autospec=True)
@patch('app_LyfeSync.views.selfcare_views.Dicas', autospec=True)
@patch('app_LyfeSync.views.selfcare_views.HumorTipo', autospec=True)
@patch('app_LyfeSync.views.selfcare_views.Humor', autospec=True)
class TestSelfCareViews(BaseViewTest):
    
    def test_autocuidado_get(self, MockHumor, MockHumorTipo, MockDicas, MockGratidao, MockAfirmacao):
        from app_LyfeSync.views.selfcare_views import autocuidado
        
        mock_afirmacoes = [MockAfirmacao(i, self.user, self.hoje, f'Afirmação {i}') for i in range(5)]
        MockAfirmacao.objects.filter.return_value.order_by.return_value = mock_afirmacoes
        
        request = self._get_request('GET', reverse('autocuidado'))
        response = autocuidado(request)
        
        self.assertEqual(response.status_code, 200)
        MockAfirmacao.objects.filter.assert_called_once_with(usuario=self.user)
        self.assertIn('afirmacoes', response.context)
        self._simulate_login_required(autocuidado, reverse('autocuidado'))

    # --- Testes de Humor ---
    
    @patch('app_LyfeSync.views.selfcare_views.Dicas.objects.filter', autospec=True)
    def test_humor_get_com_registro_e_nova_dica(self, MockDicasFilter, MockHumor, MockHumorTipo, MockDicas, MockGratidao, MockAfirmacao):
        from app_LyfeSync.views.selfcare_views import humor
        
        # 1. Mock do Humor de Hoje (sem dica salva)
        humor_hoje = MockHumor(1, self.user, self.hoje, TIPO_TRISTE, descricaohumor='Estou mal')
        MockHumor.objects.select_related.return_value.get.return_value = humor_hoje
        
        # 2. Mock da Rotação de Dica (encontra uma nova dica)
        nova_dica = MockDicas(10, 'Dica Top', 'Dica triste', TIPO_TRISTE)
        MockDicasFilter.return_value.exclude.return_value.order_by.return_value.exists.return_value = True
        MockDicasFilter.return_value.exclude.return_value.order_by.return_value.first.return_value = nova_dica
        
        # 3. Mock do Histórico Recente (vazio)
        MockHumor.objects.select_related.return_value.filter.return_value.exclude.return_value.order_by.return_value = []
        MockHumorTipo.objects.all.return_value = [TIPO_FELIZ, TIPO_TRISTE]
        
        request = self._get_request('GET', reverse('humor'))
        response = humor(request)
        
        self.assertEqual(response.status_code, 200)
        self.assertIn('dica_do_dia', response.context)
        self.assertEqual(response.context['dica_do_dia'].pk, 10)
        
        # Verifica se o Humor de hoje foi salvo (Persistência Final)
        humor_hoje.save.assert_called_once()
        # Verifica se a nova descrição inclui a tag
        MOCK_SELFCARE_FUNCTIONS['rebuild_descricaohumor'].assert_called_with(10, 'Estou mal')
        self.assertTrue(humor_hoje.descricaohumor.startswith('[DICA ID:'))
        
    def test_registrar_humor_post_success(self, MockHumor, MockHumorTipo, MockDicas, MockGratidao, MockAfirmacao):
        from app_LyfeSync.views.selfcare_views import registrar_humor
        
        mock_form_instance = MagicMock()
        mock_form_instance.save.return_value = mock_form_instance
        MOCK_FORMS['HumorForm'].return_value = MagicMock(
            is_valid=lambda: True, 
            save=MagicMock(return_value=mock_form_instance)
        )
        
        request = self._get_request('POST', reverse('registrar_humor'), data={'estado': TIPO_FELIZ.pk})
        response = registrar_humor(request)
        
        mock_form_instance.save.assert_called_once() # Salva o objeto (sem commit=False)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('humor'))
        self.assertIn('sucesso', self._get_messages(response))

    def test_alterar_humor_post_estado_change_resets_dica(self, MockHumor, MockHumorTipo, MockDicas, MockGratidao, MockAfirmacao):
        from app_LyfeSync.views.selfcare_views import alterar_humor
        
        # Humor Existente com TIPO_TRISTE e uma dica salva (ID: 10)
        humor_existente = MockHumor(1, self.user, self.hoje, TIPO_TRISTE, descricaohumor='[DICA ID:10] Desc Antiga')
        MockHumor.objects.filter.return_value.get.return_value = humor_existente
        
        # Mock do form que muda o estado para FELIZ
        MockHumor.objects.get.return_value = humor_existente
        form_mock = MagicMock(is_valid=lambda: True)
        form_mock.cleaned_data = {'estado': TIPO_FELIZ, 'descricaohumor': 'Desc Nova'}
        form_mock.save.return_value = humor_existente # Simula save(commit=False)
        
        # Novo Humor Form que simula o objeto Humor com o novo estado
        MOCK_FORMS['HumorForm'].return_value = form_mock
        
        MOCK_SELFCARE_FUNCTIONS['extract_dica_info'].return_value = (10, 'Desc Antiga') # Dica é extraída (ID 10)
        
        request = self._get_request('POST', reverse('alterar_humor', args=[1]), data={'estado': TIPO_FELIZ.pk, 'descricaohumor': 'Desc Nova'})
        response = alterar_humor(request, 1)

        self.assertEqual(response.status_code, 302)
        # Verifica se o ID da dica foi zerado na reconstrução (10 != TIPO_FELIZ)
        MOCK_SELFCARE_FUNCTIONS['rebuild_descricaohumor'].assert_called_with(None, 'Desc Nova') 
        humor_existente.save.assert_called_once()
        self.assertIn('sucesso', self._get_messages(response))
        
    def test_delete_humor_post_success(self, MockHumor, MockHumorTipo, MockDicas, MockGratidao, MockAfirmacao):
        from app_LyfeSync.views.selfcare_views import delete_humor
        
        humor_existente = MockHumor(1, self.user, self.hoje, TIPO_TRISTE, descricaohumor='')
        MockHumor.objects.get.return_value = humor_existente
        
        request = self._get_request('POST', reverse('delete_humor', args=[1]))
        response = delete_humor(request, 1)
        
        humor_existente.delete.assert_called_once()
        self.assertEqual(response.status_code, 302)
        self.assertIn('excluído com sucesso', self._get_messages(response))

    def test_load_humor_by_date_ajax_found(self, MockHumor, MockHumorTipo, MockDicas, MockGratidao, MockAfirmacao):
        from app_LyfeSync.views.selfcare_views import load_humor_by_date
        
        target_date = date(2024, 1, 1)
        humor_registro = MockHumor(1, self.user, target_date, TIPO_FELIZ, descricaohumor='[DICA ID:10] Texto do Usuário')
        MockHumor.objects.select_related.return_value.get.return_value = humor_registro
        
        # O mock de extract_dica_info irá limpar a descrição
        MOCK_SELFCARE_FUNCTIONS['extract_dica_info'].return_value = (10, 'Texto do Usuário')

        request = self._get_request('GET', reverse('load_humor_by_date'), data={'date': '2024-01-01'})
        response = load_humor_by_date(request)
        
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response, JsonResponse)
        data = response.json()
        self.assertTrue(data['exists'])
        self.assertEqual(data['descricaohumor'], 'Texto do Usuário')
        
    # --- Testes de Dicas (Admin/Staff) ---
    
    @patch('app_LyfeSync.views.selfcare_views.DICAS_POR_PAGINA', 1)
    def test_registrar_dica_staff_get_pagination(self, MockHumor, MockHumorTipo, MockDicas, MockGratidao, MockAfirmacao):
        from app_LyfeSync.views.selfcare_views import registrar_dica
        
        # Cria 3 dicas para testar a paginação (DICAS_POR_PAGINA = 1)
        mock_dicas_list = [MockDicas(i, f'Dica {i}', f'Desc {i}', TIPO_FELIZ) for i in range(1, 4)]
        MockDicas.objects.all.return_value.order_by.return_value = mock_dicas_list
        MockHumorTipo.objects.all.return_value.order_by.return_value = [TIPO_FELIZ]
        
        request = self._get_request('GET', reverse('registrar_dica'), user=self.staff_user, data={'page': 2})
        response = registrar_dica(request)
        
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context['page_obj'].has_next())
        self.assertEqual(response.context['page_obj'].number, 2)
        self.assertEqual(response.context['page_obj'].object_list[0].nomeDica, 'Dica 2')
        
    def test_registrar_dica_non_staff_redirects(self, *mocks):
        from app_LyfeSync.views.selfcare_views import registrar_dica
        request = self._get_request('GET', reverse('registrar_dica'), user=self.user)
        response = registrar_dica(request)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, '/')
    
    def test_excluir_dica_staff_success(self, MockHumor, MockHumorTipo, MockDicas, MockGratidao, MockAfirmacao):
        from app_LyfeSync.views.selfcare_views import excluir_dica
        
        dica_existente = MockDicas(1, 'Dica a Excluir', 'Desc', TIPO_FELIZ)
        MockDicas.objects.get.return_value = dica_existente
        
        request = self._get_request('POST', reverse('excluir_dica', args=[1]), user=self.staff_user)
        response = excluir_dica(request, 1)
        
        dica_existente.delete.assert_called_once()
        self.assertEqual(response.status_code, 302)
        self.assertIn('excluída com sucesso', self._get_messages(response))

    # --- Testes de Gratidão ---

    @patch('app_LyfeSync.views.selfcare_views.GRATITUDE_PER_PAGE', 1)
    def test_gratidao_get_pagination(self, MockHumor, MockHumorTipo, MockDicas, MockGratidao, MockAfirmacao):
        from app_LyfeSync.views.selfcare_views import gratidao
        
        MockGratidao.objects.filter.return_value.order_by.return_value = [
            MockGratidao(i, self.user, self.hoje - timedelta(days=i), f'G{i}') for i in range(1, 5)
        ]
        MockGratidao.objects.filter.return_value = MockGratidao.objects.filter.return_value # Mock do exclude também
        MockGratidao.objects.filter.return_value.exclude.return_value.order_by.return_value = MockGratidao.objects.filter.return_value.order_by.return_value

        request = self._get_request('GET', reverse('gratidao'), data={'page': 3})
        response = gratidao(request)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['page_obj'].number, 3)
        self.assertEqual(response.context['page_obj'].object_list[0].descricaogratidao, 'G3')
        
    def test_registrar_gratidao_post_success(self, MockHumor, MockHumorTipo, MockDicas, MockGratidao, MockAfirmacao):
        from app_LyfeSync.views.selfcare_views import registrar_gratidao
        
        request = self._get_request('POST', reverse('registrar_gratidao'), data={'data': self.hoje, 'descricao_1': 'Gratidão teste'})
        response = registrar_gratidao(request)
        
        MOCK_FORMS['GratidaoCreateForm'].return_value.save.assert_called_once()
        self.assertEqual(response.status_code, 302)
        self.assertIn('Sucesso!', self._get_messages(response))

    def test_alterar_gratidao_post_success(self, MockHumor, MockHumorTipo, MockDicas, MockGratidao, MockAfirmacao):
        from app_LyfeSync.views.selfcare_views import alterar_gratidao
        
        gratidao_obj = MockGratidao(1, self.user, self.hoje, 'Descricao Antiga')
        MockGratidao.objects.get.return_value = gratidao_obj
        
        MOCK_FORMS['GratidaoUpdateForm'].return_value = MagicMock(
            is_valid=lambda: True, 
            cleaned_data={'descricaogratidao': 'Nova Gratidão\ncom quebra de linha'},
            save=MagicMock(return_value=gratidao_obj)
        )
        
        request = self._get_request('POST', reverse('alterar_gratidao', args=[1]), data={'descricaogratidao': 'Nova Gratidão'})
        response = alterar_gratidao(request, 1)

        gratidao_obj.save.assert_called_once()
        self.assertEqual(response.status_code, 302)
        # Verifica se a mensagem usa o título curto gerado ('Nova Gratidão')
        self.assertIn('alterada com sucesso', self._get_messages(response)[0])

    def test_delete_gratidao_post_success(self, MockHumor, MockHumorTipo, MockDicas, MockGratidao, MockAfirmacao):
        from app_LyfeSync.views.selfcare_views import delete_gratidao
        
        gratidao_obj = MockGratidao(1, self.user, self.hoje, 'Minha Gratidao')
        MockGratidao.objects.get.return_value = gratidao_obj
        
        request = self._get_request('POST', reverse('delete_gratidao', args=[1]))
        response = delete_gratidao(request, 1)
        
        gratidao_obj.delete.assert_called_once()
        self.assertEqual(response.status_code, 302)
        self.assertIn('"Minha Gratidao" excluída com sucesso', self._get_messages(response))

    # --- Testes de Afirmação ---

    @patch('app_LyfeSync.views.selfcare_views.AFIRMACOES_POR_PAGINA', 1)
    def test_afirmacao_get_pagination(self, MockHumor, MockHumorTipo, MockDicas, MockGratidao, MockAfirmacao):
        from app_LyfeSync.views.selfcare_views import afirmacao
        
        MockAfirmacao.objects.filter.return_value.order_by.return_value = [
            MockAfirmacao(i, self.user, self.hoje - timedelta(days=i), f'A{i}') for i in range(1, 5)
        ]

        request = self._get_request('GET', reverse('afirmacao'), data={'page': 4})
        response = afirmacao(request)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['page_obj'].number, 4)
        self.assertEqual(response.context['page_obj'].object_list[0].descricaoafirmacao, 'A4')
        
    @patch('app_LyfeSync.views.selfcare_views.transaction')
    @patch('app_LyfeSync.views.selfcare_views.Afirmacao.objects.bulk_create', autospec=True)
    def test_registrar_afirmacao_post_bulk_create_success(self, mock_bulk_create, mock_transaction, MockHumor, MockHumorTipo, MockDicas, MockGratidao, MockAfirmacao):
        from app_LyfeSync.views.selfcare_views import registrar_afirmacao
        
        request = self._get_request('POST', reverse('registrar_afirmacao'), data={'data': self.hoje, 'descricao_1': 'A1', 'descricao_2': 'A2', 'descricao_3': ''})
        response = registrar_afirmacao(request)
        
        # Verifica se o bulk_create foi chamado com 2 objetos (A1, A2)
        mock_bulk_create.assert_called_once()
        self.assertEqual(len(mock_bulk_create.call_args[0][0]), 2)
        
        self.assertEqual(response.status_code, 302)
        self.assertIn('2 Afirmação(ões) registrada(s) com sucesso', self._get_messages(response))

    def test_alterar_afirmacao_post_success(self, MockHumor, MockHumorTipo, MockDicas, MockGratidao, MockAfirmacao):
        from app_LyfeSync.views.selfcare_views import alterar_afirmacao
        
        afirmacao_obj = MockAfirmacao(1, self.user, self.hoje, 'Afirmacao Antiga')
        MockAfirmacao.objects.get.return_value = afirmacao_obj
        
        request = self._get_request('POST', reverse('alterar_afirmacao', args=[1]), data={'descricaoafirmacao': 'Afirmacao Nova'})
        response = alterar_afirmacao(request, 1)

        afirmacao_obj.save.assert_called_once()
        self.assertEqual(afirmacao_obj.descricaoafirmacao, 'Afirmacao Nova')
        self.assertEqual(response.status_code, 302)
        self.assertIn('alterada com sucesso', self._get_messages(response))

# --- TESTES PARA app_LyfeSync/views/reports_views.py ---

# Os mocks de reports_views.py usam os mesmos models, mas também precisam do patch de Forms de Relatório e Funções Auxiliares.
@patch.dict('app_LyfeSync.views.reports_views.__builtins__', {'RelatorioHabitoForm': MOCK_FORMS['RelatorioHabitoForm']}, clear=False)
@patch.dict('app_LyfeSync.views.reports_views.__builtins__', MOCK_REPORT_FUNCTIONS, clear=False)
@patch('app_LyfeSync.views.reports_views.Gratidao', autospec=True)
@patch('app_LyfeSync.views.reports_views.Afirmacao', autospec=True)
@patch('app_LyfeSync.views.reports_views.StatusDiario', autospec=True)
@patch('app_LyfeSync.views.reports_views.Habito', autospec=True)
@patch('app_LyfeSync.views.reports_views.HumorTipo', autospec=True)
@patch('app_LyfeSync.views.reports_views.Humor', autospec=True)
class TestReportViews(BaseViewTest):
    
    def test_relatorios_get(self, *mocks):
        from app_LyfeSync.views.reports_views import relatorios
        
        request = self._get_request('GET', reverse('relatorios'))
        response = relatorios(request)
        self.assertEqual(response.status_code, 200)

    def test_relatorio_habito_get_success(self, MockHumor, MockHumorTipo, MockHabito, MockStatusDiario, *mocks):
        from app_LyfeSync.views.reports_views import relatorio_habito
        
        # Mocks para Habito e StatusDiario
        habito1 = MockHabito(1, self.user, 'Correr', date(2023, 1, 1))
        habito2 = MockHabito(2, self.user, 'Ler', date(2024, 1, 1))
        MockHabito.objects.filter.return_value.order_by.return_value = [habito1, habito2]

        MockStatusDiario.objects.filter.return_value.values.return_value = [
            {'habito_id': 1, 'data__day': 10}, # Habito 1 concluído no dia 10
            {'habito_id': 1, 'data__day': 11},
            {'habito_id': 2, 'data__day': 5},  # Habito 2 concluído no dia 5
        ]
        
        # O RelatorioHabitoForm já está mockado para retornar mes=1, ano=2024
        request = self._get_request('GET', reverse('relatorio_habito'))
        response = relatorio_habito(request)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['dados_relatorio']), 2)
        # Verifica a contagem do primeiro hábito (dia 10 e 11)
        self.assertEqual(response.context['dados_relatorio'][0]['total_concluido'], 2)
        
    def test_exportar_habito_csv_success(self, *mocks):
        from app_LyfeSync.views.reports_views import exportar_habito_csv
        
        request = self._get_request('GET', reverse('exportar_habito_csv'))
        response = exportar_habito_csv(request)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'text/csv')
        
        # Verifica se a função auxiliar de busca de dados foi chamada
        MOCK_REPORT_FUNCTIONS['get_habitos_e_acompanhamento'].assert_called_once()
        
    def test_exportar_gratidao_pdf_success(self, MockAfirmacao, MockGratidao, *mocks):
        from app_LyfeSync.views.reports_views import exportar_gratidao_pdf
        
        MockGratidao.objects.filter.return_value.order_by.return_value = [
            MockGratidao(1, self.user, date(2024, 1, 15), 'Gratidão do Meio'),
        ]

        request = self._get_request('GET', reverse('exportar_gratidao_pdf'))
        response = exportar_gratidao_pdf(request)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/pdf')
        # Verifica se a função auxiliar de conversão foi chamada
        MOCK_REPORT_FUNCTIONS['convert_html_to_pdf'].assert_called_once()

    def test_relatorio_humor_get_success(self, MockHumor, MockHumorTipo, *mocks):
        from app_LyfeSync.views.reports_views import relatorio_humor
        
        # Mocks para o helper _get_report_context
        mock_context = {
            'mes': 1, 'ano': 2024, 'dias_do_mes': range(1, 32),
            'report_data': [{'tipo': TIPO_FELIZ, 'total': 5, 'dias': {1: True}}],
            'total_dias_registrados': 5,
        }
        
        with patch('app_LyfeSync.views.reports_views._get_report_context', return_value=mock_context) as mock_get_context:
            request = self._get_request('GET', reverse('relatorio_humor'))
            response = relatorio_humor(request)
            
            self.assertEqual(response.status_code, 200)
            mock_get_context.assert_called_once()
            self.assertIn('report_data', response.context)

    def test_exportar_humor_csv_success(self, *mocks):
        from app_LyfeSync.views.reports_views import exportar_humor_csv
        
        # Mock para o helper _get_report_context
        mock_context = {
            'dias_do_mes': range(1, 4),
            'report_data': [{'tipo': TIPO_FELIZ, 'total': 2, 'dias': {1: True, 2: False, 3: True}}],
        }
        
        with patch('app_LyfeSync.views.reports_views._get_report_context', return_value=mock_context):
            request = self._get_request('GET', reverse('exportar_humor_csv', args=[1, 2024]))
            response = exportar_humor_csv(request, 1, 2024)
            
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response['Content-Type'], 'text/csv')
            
            content = response.content.decode('utf-8').strip().split('\r\n')
            # Verifica o cabeçalho
            self.assertIn('Humor;1;2;3;Total no Mês', content[0]) 
            # Verifica a linha de dados (Feliz, dia 1=X, dia 2=, dia 3=X, Total=2)
            self.assertIn('Feliz;X;;X;2', content[1])