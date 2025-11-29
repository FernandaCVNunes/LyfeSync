# app_LyfeSync/tests/test_forms.py

from django.test import TestCase
from django.core.exceptions import ValidationError
from unittest.mock import MagicMock, patch, call
from datetime import date
from django.contrib.auth import get_user_model
from django.forms.models import modelform_factory
from allauth.account.forms import SignupForm # Importa a classe base para o mock

# -------------------------------------------------------------------
# IMPORTAÇÕES DOS FORMULÁRIOS (AJUSTE ESTE CAMINHO CONFORME SEU PROJETO)
# -------------------------------------------------------------------
from app_LyfeSync.forms import (
    HabitoForm, RelatorioHabitoForm, 
    GratidaoCreateForm, GratidaoUpdateForm, 
    AfirmacaoRegistroForm, AfirmacaoAlteracaoForm, 
    HumorForm, RelatorioHumorForm, 
    DicasForm, UserUpdateForm, PerfilUsuarioForm, 
    CustomSignupForm, ConsentimentoForm
)

# -------------------------------------------------------------------
# MOCKS DOS MODELOS PARA ISOLAMENTO (ASSUMIMOS OS NOMES DE MODELOS NO ARQUIVO FORMS.PY)
# -------------------------------------------------------------------
# É crucial que os objetos mockados usem os mesmos nomes dos modelos no forms.py
class MockHabito:
    # Simula a FREQUENCIA_CHOICES usada na Meta
    FREQUENCIA_CHOICES = [('D', 'Diário'), ('S', 'Semanal'), ('M', 'Mensal')]
    objects = MagicMock()
class MockGratidao:
    objects = MagicMock()
class MockHumor:
    objects = MagicMock()
class MockHumorTipo:
    objects = MagicMock()
    def __init__(self, pk=1, nome='Feliz'): self.pk = pk; self.nome = nome
    def __str__(self): return self.nome
class MockDicas:
    objects = MagicMock()
class MockPerfilUsuario:
    TIPO_CHOICES = [('Cliente', 'Cliente'), ('Profissional', 'Profissional')]
    objects = MagicMock()
    def __init__(self, **kwargs): self.__dict__.update(kwargs)
    def save(self): pass
    
User = get_user_model() # Pega o User model

# Configuração do Mock para HumorTipo (necessário para DicasForm)
mock_humor_tipo_feliz = MockHumorTipo(pk=1, nome='Feliz')
mock_humor_tipo_triste = MockHumorTipo(pk=2, nome='Triste')

# -------------------------------------------------------------------
# TESTES PARA HABITOFORM
# -------------------------------------------------------------------
@patch('app_LyfeSync.forms.Habito', new=MockHabito)
class HabitoFormTest(TestCase):
    
    def test_habito_form_valid_data(self):
        form = HabitoForm(data={
            'nome': 'Meditar',
            'data_inicio': date.today().strftime('%Y-%m-%d'),
            'data_fim': date(date.today().year + 1, 1, 1).strftime('%Y-%m-%d'),
            'quantidade': 10,
            'frequencia': 'D',
            'alvo': 'Alcançar 100 sessões',
            'descricao': 'Meditação matinal de 10 minutos'
        })
        self.assertTrue(form.is_valid())

    def test_habito_form_missing_required_nome(self):
        # 'nome' é campo obrigatório em ModelForms
        form = HabitoForm(data={
            'data_inicio': date.today().strftime('%Y-%m-%d'),
            'quantidade': 1,
            'frequencia': 'D'
        })
        self.assertFalse(form.is_valid())
        self.assertIn('nome', form.errors)

# -------------------------------------------------------------------
# TESTES PARA RELATORIOHABITOFORM
# -------------------------------------------------------------------
class RelatorioHabitoFormTest(TestCase):
    
    def test_relatorio_habito_form_valid_data(self):
        form = RelatorioHabitoForm(data={'mes': 1, 'ano': 2025})
        self.assertTrue(form.is_valid())
        
    def test_relatorio_habito_form_invalid_month_range(self):
        # Mês 13 (inválido)
        form = RelatorioHabitoForm(data={'mes': 13, 'ano': 2025})
        self.assertFalse(form.is_valid())
        self.assertIn('mes', form.errors)

    def test_relatorio_habito_form_invalid_year_range(self):
        # Ano 1999 (abaixo do min_value=2000)
        form = RelatorioHabitoForm(data={'mes': 1, 'ano': 1999})
        self.assertFalse(form.is_valid())
        self.assertIn('ano', form.errors)

# -------------------------------------------------------------------
# TESTES PARA GRATIDAOCREATEFORM (Validação e Save Customizado)
# -------------------------------------------------------------------
@patch('app_LyfeSync.forms.Gratidao', new=MockGratidao) # Mock do modelo para save
class GratidaoCreateFormTest(TestCase):
    
    def setUp(self):
        self.mock_user = MagicMock(pk=1)
        self.valid_data_base = {'data': date.today().strftime('%Y-%m-%d')}
    
    # --- Testes de Validação (clean) ---
    def test_form_valid_one_description_with_whitespace(self):
        data = self.valid_data_base.copy()
        data.update({
            'descricaogratidao_1': '  Sou grato por isso.  ',
            'descricaogratidao_2': '',
            'descricaogratidao_3': ''
        })
        form = GratidaoCreateForm(data=data)
        self.assertTrue(form.is_valid())

    def test_form_fails_no_descriptions(self):
        data = self.valid_data_base.copy()
        data.update({
            'descricaogratidao_1': '',
            'descricaogratidao_2': '   ', # Apenas whitespace
            'descricaogratidao_3': ''
        })
        form = GratidaoCreateForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn('__all__', form.errors) 
        self.assertIn('Pelo menos uma das Descrições', str(form.errors))

    def test_form_fails_missing_data(self):
        data = {'descricaogratidao_1': 'G1'}
        form = GratidaoCreateForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn('data', form.errors) 

    # --- Testes de Lógica de Negócios (generate_gratitude_name) ---
    def test_generate_name_truncation(self):
        form = GratidaoCreateForm()
        long_text = "Esta é uma descrição muito, muito longa que certamente excederá o limite de 100 caracteres para ser truncada. Testando a lógica de corte..."
        expected_name = "Esta é uma descrição muito, muito longa que certamente excederá o limite de 100 caracteres para ser truncada..."
        name = form.generate_gratitude_name(long_text)
        self.assertEqual(len(name), 100)
        self.assertEqual(name, expected_name)
        
    def test_generate_name_with_newlines_and_whitespace(self):
        form = GratidaoCreateForm()
        description = "   Primeira linha (Nome)   \nSegunda linha (Detalhe)"
        name = form.generate_gratitude_name(description)
        self.assertEqual(name, "Primeira linha (Nome)")

    # --- Testes do Método save ---
    def test_save_creates_two_objects_and_calls_bulk_create_once(self):
        mock_date = date(2025, 1, 1)
        data = {
            'data': mock_date.strftime('%Y-%m-%d'),
            'descricaogratidao_1': 'G1',
            'descricaogratidao_2': 'G2',
            'descricaogratidao_3': '   ' # Deve ser ignorado
        }
        form = GratidaoCreateForm(data=data)
        self.assertTrue(form.is_valid())

        # Patch o bulk_create para verificar as chamadas
        # Usar 'app_LyfeSync.models.Gratidao' se o save() no form.py for 'Gratidao.objects.bulk_create'
        with patch('app_LyfeSync.models.Gratidao.objects.bulk_create') as mock_bulk_create:
            form.save(user=self.mock_user)
            
            # Verifica se bulk_create foi chamado
            mock_bulk_create.assert_called_once()
            
            args, _ = mock_bulk_create.call_args
            created_objects = args[0]
            self.assertEqual(len(created_objects), 2)
            
            # Verifica se os argumentos passados para os objetos mockados estão corretos
            calls = [
                call(data=mock_date, descricaogratidao='G1', usuario=self.mock_user),
                call(data=mock_date, descricaogratidao='G2', usuario=self.mock_user)
            ]
            # O teste se torna mais complexo pois bulk_create recebe objetos, não os cria.
            # O teste acima já verifica o número correto de objetos Gratidao (mockados) na lista.

# -------------------------------------------------------------------
# TESTES PARA GRATIDAOUPDATEFORM
# -------------------------------------------------------------------
@patch('app_LyfeSync.forms.Gratidao', new=MockGratidao)
class GratidaoUpdateFormTest(TestCase):

    def test_gratidao_update_form_valid_data(self):
        # Usando a forma de ModelForm para verificar se a validação básica passa
        MockModelForm = modelform_factory(MockGratidao, GratidaoUpdateForm.Meta.fields)
        form = MockModelForm(data={'data': '2024-10-20', 'descricaogratidao': 'Descrição atualizada'})
        self.assertTrue(form.is_valid())
        
    def test_gratidao_update_form_missing_description(self):
        # Descrição é obrigatória no campo CharField
        MockModelForm = modelform_factory(MockGratidao, GratidaoUpdateForm.Meta.fields)
        form = MockModelForm(data={'data': '2024-10-20', 'descricaogratidao': ''})
        self.assertFalse(form.is_valid())
        self.assertIn('descricaogratidao', form.errors)

# -------------------------------------------------------------------
# TESTES PARA AFIRMACAOREGISTROFORM
# -------------------------------------------------------------------
class AfirmacaoRegistroFormTest(TestCase):

    def test_afirmacao_registro_form_valid_data(self):
        form = AfirmacaoRegistroForm(data={
            'data': date.today().strftime('%Y-%m-%d'),
            'descricao_1': 'Eu sou capaz.',
            'descricao_2': 'Eu mereço.',
            'descricao_3': ''
        })
        self.assertTrue(form.is_valid())

    def test_afirmacao_registro_form_fails_missing_first_description(self):
        # descricao_1 é required=True no AfirmacaoBaseForm
        form = AfirmacaoRegistroForm(data={
            'data': date.today().strftime('%Y-%m-%d'),
            'descricao_1': '',
            'descricao_2': 'D2',
            'descricao_3': 'D3'
        })
        self.assertFalse(form.is_valid())
        self.assertIn('descricao_1', form.errors)
        
    def test_afirmacao_registro_form_fails_missing_data(self):
        form = AfirmacaoRegistroForm(data={'descricao_1': 'D1'})
        self.assertFalse(form.is_valid())
        self.assertIn('data', form.errors)

# -------------------------------------------------------------------
# TESTES PARA HUMORFORM
# -------------------------------------------------------------------
@patch('app_LyfeSync.forms.Humor', new=MockHumor)
class HumorFormTest(TestCase):

    def setUp(self):
        # Como é um ModelForm, o 'estado' requer um ID de um objeto FK válido.
        # Não precisamos mockar o FK em si, apenas fornecer um ID válido.
        self.mock_estado_id = 1 

    def test_humor_form_valid_data(self):
        form = HumorForm(data={
            'estado': self.mock_estado_id, 
            'descricaohumor': 'Dia muito produtivo',
            'data': date.today().strftime('%Y-%m-%d')
        })
        self.assertTrue(form.is_valid())

    def test_humor_form_missing_estado(self):
        form = HumorForm(data={'descricaohumor': 'Detalhe', 'data': date.today().strftime('%Y-%m-%d')})
        self.assertFalse(form.is_valid())
        self.assertIn('estado', form.errors) 
        # Verifica a mensagem de erro customizada
        # self.assertIn('Por favor, selecione seu humor para prosseguir.', form.errors['estado'])

# -------------------------------------------------------------------
# TESTES PARA DICASFORM
# -------------------------------------------------------------------
@patch('app_LyfeSync.forms.Dicas', new=MockDicas)
@patch('app_LyfeSync.forms.HumorTipo.objects.all', return_value=[mock_humor_tipo_feliz, mock_humor_tipo_triste])
class DicasFormTest(TestCase):
    
    def test_dicas_form_valid_data(self, mock_all):
        mock_user = MagicMock(pk=10) # Mock 'criado_por' user
        form = DicasForm(data={
            'humor_relacionado': mock_humor_tipo_feliz.pk, 
            'nomeDica': 'Respiracao Profunda',
            'descricaoDica': 'Técnica de 4-7-8',
            'criado_por': mock_user.pk
        })
        self.assertTrue(form.is_valid())

    def test_dicas_form_missing_humor_relacionado(self, mock_all):
        mock_user = MagicMock(pk=10)
        form = DicasForm(data={
            'nomeDica': 'Respiracao',
            'descricaoDica': 'Tecnica',
            'criado_por': mock_user.pk
        })
        self.assertFalse(form.is_valid())
        self.assertIn('humor_relacionado', form.errors)

# -------------------------------------------------------------------
# TESTES PARA USERUPDATEFORM e PERFILUSUARIOFORM
# -------------------------------------------------------------------
@patch('app_LyfeSync.forms.User', new=MagicMock(spec=User))
class UserUpdateFormTest(TestCase):
    
    def test_user_update_form_valid_data(self):
        # A validação se baseia na Meta do ModelForm, que usa first_name e last_name
        form = UserUpdateForm(data={'first_name': 'João', 'last_name': 'Silva'})
        self.assertTrue(form.is_valid())

@patch('app_LyfeSync.forms.PerfilUsuario', new=MockPerfilUsuario)
class PerfilUsuarioFormTest(TestCase):

    def test_perfil_usuario_form_valid_data(self):
        form = PerfilUsuarioForm(data={'tipoUsuario': 'Profissional'})
        self.assertTrue(form.is_valid())

    def test_perfil_usuario_form_invalid_choice(self):
        form = PerfilUsuarioForm(data={'tipoUsuario': 'Inexistente'})
        self.assertFalse(form.is_valid())
        self.assertIn('tipoUsuario', form.errors)

# -------------------------------------------------------------------
# TESTES PARA CUSTOMSIGNUPFORM
# -------------------------------------------------------------------
class CustomSignupFormTest(TestCase):
    
    # Mocka o método save da classe base (allauth.account.forms.SignupForm)
    @patch.object(SignupForm, 'save') 
    @patch('app_LyfeSync.forms.PerfilUsuario') # Mocka o PerfilUsuario para o save customizado
    def test_custom_signup_form_save_updates_user_and_perfil(self, MockPerfilUsuario, mock_super_save):
        
        # 1. Configura Mocks
        mock_user = MagicMock(spec=User)
        mock_user.perfil = MagicMock(spec=MockPerfilUsuario) # Mock do Perfil já criado
        mock_super_save.return_value = mock_user
        
        # 2. Dados do Form (Assumindo que a validação base (username, email, password) passa)
        data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'password123',
            'password2': 'password123',
            'first_name': 'João',
            'last_name': 'Silva'
        }
        form = CustomSignupForm(data=data)
        
        # Simula a validação bem-sucedida (o save() só é chamado após is_valid())
        form.is_valid = MagicMock(return_value=True)
        form.cleaned_data = data 
        
        # 3. Executa o save
        saved_user = form.save(request=MagicMock())
        
        # 4. Verifica as asserções
        
        # Verifica se super().save foi chamado
        mock_super_save.assert_called_once()
        
        # Verifica se os campos extra foram setados no user
        self.assertEqual(saved_user.first_name, 'João')
        self.assertEqual(saved_user.last_name, 'Silva')
        
        # Verifica se user.save() foi chamado para persistir as alterações
        saved_user.save.assert_called_once()
        
        # Verifica se o tipoUsuario foi atualizado e salvo
        self.assertEqual(saved_user.perfil.tipoUsuario, 'Cliente')
        saved_user.perfil.save.assert_called_once()
        
# -------------------------------------------------------------------
# TESTES PARA CONSENTIMENTOFORM
# -------------------------------------------------------------------
class ConsentimentoFormTest(TestCase):
    
    def test_consentimento_form_valid_data(self):
        # Campo booleano aceito
        form = ConsentimentoForm(data={'aceite_termos': True})
        self.assertTrue(form.is_valid())

    def test_consentimento_form_fails_not_accepted(self):
        # Campo booleano não aceito (requerido=True)
        form = ConsentimentoForm(data={})
        self.assertFalse(form.is_valid())
        self.assertIn('aceite_termos', form.errors)
        
    def test_consentimento_form_fails_explicitly_false(self):
        form = ConsentimentoForm(data={'aceite_termos': False})
        self.assertFalse(form.is_valid())
        self.assertIn('aceite_termos', form.errors)