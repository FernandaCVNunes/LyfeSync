# Este arquivo contém os Formulários do Django, usados para renderização
# HTML, validação e personalização da interface de administração.

from django import forms
from django.utils import timezone
from django.forms import ModelForm, TextInput, DateInput, NumberInput, Select, Textarea, RadioSelect
from django.contrib.auth.forms import UserChangeForm
# ALTERAÇÃO: Usar get_user_model é uma boa prática para garantir compatibilidade
from django.contrib.auth import get_user_model
from allauth.account.forms import SignupForm
from django.db import transaction

# Importação dos modelos, assumindo que eles existem no diretório pai ou estão configurados
# NOTA: O nome dos modelos aqui é baseado na estrutura do Forms e não nos Models anteriormente vistos.
from .models import Habito, Gratidao, Afirmacao, Humor, Dicas, PerfilUsuario

# Obtém o modelo de Usuário ativo (padrão ou customizado)
User = get_user_model()

# -------------------------------------------------------------------
# 1. FORMULÁRIO DE HÁBITO
# -------------------------------------------------------------------

class HabitoForm(forms.ModelForm):
    """
    Formulário para a criação e edição de hábitos.
    """
    class Meta:
        model = Habito
        fields = ['nome', 'data_inicio', 'data_fim', 'quantidade', 'frequencia', 'alvo', 'descricao']
        
        widgets = {
            'nome': TextInput(attrs={'placeholder': 'Ex: Beber água, Meditar', 'class': 'form-control'}),
            'data_inicio': DateInput(
                attrs={'type': 'date', 'class': 'form-control', 'value': timezone.localdate().strftime('%Y-%m-%d')},
                format='%Y-%m-%d'
            ),
            'data_fim': DateInput(
                attrs={'type': 'date', 'class': 'form-control'},
                format='%Y-%m-%d'
            ),
            'quantidade': NumberInput(attrs={'placeholder': 'Ex: 8 copos, 10 minutos', 'min': 1, 'class': 'form-control'}),
            'frequencia': Select(
                choices=[('Diário', 'Diário'), ('Semanal', 'Semanal'), ('Mensal', 'Mensal')],
                attrs={'class': 'form-control'}
            ),
            'alvo': TextInput(attrs={'placeholder': 'Ex: Chegar a 50kg, 100% de conclusão', 'class': 'form-control'}),
            'descricao': Textarea(attrs={'placeholder': 'Detalhes sobre como executar o hábito', 'rows': 3, 'class': 'form-control'}),
        }
        
        labels = {
            'nome': 'Nome do Hábito',
            'data_inicio': 'Data de Início',
            'data_fim': 'Data de Fim (Opcional)',
            'quantidade': 'Quantidade/Meta Diária', 
            'frequencia': 'Frequência',
            'alvo': 'Alvo/Objetivo',
            'descricao': 'Descrição',
        }

# -------------------------------------------------------------------
# 2. FORMULÁRIOS PARA AUTOCUIDADO
# -------------------------------------------------------------------

class GratidaoForm(forms.ModelForm):
    """
    Formulário para a criação de registros de Gratidão.
    """
    class Meta:
        model = Gratidao
        fields = ['nomegratidao', 'descricaogratidao', 'data']
        widgets = {
            'nomegratidao': TextInput(attrs={'placeholder': 'Ex: Pelo Sol de hoje', 'class': 'form-control'}),
            'descricaogratidao': Textarea(attrs={'placeholder': 'Escreva sobre o que você é grato.', 'rows': 4, 'class': 'form-control'}),
            'data': DateInput(
                attrs={'type': 'date', 'class': 'form-control', 'value': timezone.localdate().strftime('%Y-%m-%d')},
                format='%Y-%m-%d'
            ),
        }
        labels = {
            'nomegratidao': 'O que te fez grato?',
            'descricaogratidao': 'Detalhes',
            'data': 'Data',
        }

class AfirmacaoForm(forms.ModelForm):
    """
    Formulário para a criação de registros de Afirmação.
    """
    class Meta:
        model = Afirmacao
        fields = ['nomeafirmacao', 'descricaoafirmacao', 'data']
        widgets = {
            'nomeafirmacao': TextInput(attrs={'placeholder': 'Ex: Sou capaz de superar desafios', 'class': 'form-control'}),
            'descricaoafirmacao': Textarea(attrs={'placeholder': 'Detalhe como esta afirmação te impacta.', 'rows': 4, 'class': 'form-control'}),
            'data': DateInput(
                attrs={'type': 'date', 'class': 'form-control', 'value': timezone.localdate().strftime('%Y-%m-%d')},
                format='%Y-%m-%d'
            ),
        }
        labels = {
            'nomeafirmacao': 'Afirmação Principal',
            'descricaoafirmacao': 'Detalhes/Intenção',
            'data': 'Data',
        }
        
class HumorForm(forms.ModelForm):
    """
    Formulário para a criação/edição de registros de Humor.
    """
    class Meta:
        model = Humor
        # O campo 'idusuario' será preenchido na view
        fields = ['estado', 'descricaohumor', 'data'] 
        
        widgets = {
            # O campo 'estado' se beneficia de um RadioSelect com as choices definidas no Model
            'estado': RadioSelect(attrs={'class': 'form-control'}), 
            'descricaohumor': Textarea(attrs={'placeholder': 'Opcional: Descreva o que motivou este humor.', 'rows': 4, 'class': 'form-control'}),
            'data': DateInput(
                attrs={'type': 'date', 'class': 'form-control', 'value': timezone.localdate().strftime('%Y-%m-%d')},
                format='%Y-%m-%d'
            ),
        }
        labels = {
            'estado': 'Qual o seu humor?',
            'descricaohumor': 'Detalhes/Motivação',
            'data': 'Data do Registro',
        }

        error_messages = {
            'estado': {
                'required': 'Por favor, selecione seu humor para prosseguir.',
            },
            'data': {
                 'required': 'A data do registro é obrigatória.',
            }
        }

class DicasForm(forms.ModelForm):
    """
    Formulário para o administrador cadastrar novas dicas de humor.
    """
    
    class Meta:
        model = Dicas
        # ASSUMIDO: Campos para corresponder ao modelo Dicas
        fields = ['TipoHumor', 'nomeDica', 'descricaoDica']
        
        widgets = {
            'TipoHumor': forms.Select(attrs={
                'class': 'form-control' 
            }),
            'nomeDica': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Digite um título curto para a dica'
            }),
            'descricaoDica': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 5, 
                'placeholder': 'Escreva aqui a descrição detalhada da dica...',
                'style': 'min-height: 200px;'
            }),
        }

# -------------------------------------------------------------------
# 3. FORMULÁRIOS DE USUÁRIO E PERFIL
# -------------------------------------------------------------------

class UserUpdateForm(UserChangeForm):
    """
    Formulário para o usuário editar seu nome e sobrenome (AuthUser).
    """
    class Meta:
        # CORREÇÃO: Usando o modelo User obtido via get_user_model()
        model = User 
        fields = ('first_name', 'last_name') 
        
        widgets = {
            'first_name': TextInput(attrs={'class': 'form-control'}),
            'last_name': TextInput(attrs={'class': 'form-control'}),
        }

    # Removemos o campo 'password' para evitar que o cliente altere a senha acidentalmente
    def __init__(self, *args, **kwargs):
        super(UserUpdateForm, self).__init__(*args, **kwargs)
        if 'password' in self.fields:
            del self.fields['password'] 
        
        # Garante que todos os campos restantes recebam a classe Bootstrap
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'form-control'})
            
# Formulário para o Perfil (Contém tipoUsuario)
class PerfilUsuarioForm(forms.ModelForm):
    """
    Formulário para o usuário alterar o tipo de perfil (Ex: Básico, Premium).
    """
    class Meta:
        model = PerfilUsuario
        fields = ('tipoUsuario',)
        
        widgets = {
             'tipoUsuario': Select(attrs={'class': 'form-select'}),
        }
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # O campo 'tipoUsuario' deve ser o único visível/editável se este formulário for usado isoladamente.


class CustomSignupForm(SignupForm):
    """
    Estende o formulário de cadastro do Django-allauth para incluir
    os campos first_name e last_name.
    """
    first_name = forms.CharField(max_length=150, label='Nome', widget=TextInput(attrs={'class': 'form-control'}))
    last_name = forms.CharField(max_length=150, label='Sobrenome', widget=TextInput(attrs={'class': 'form-control'}))

    @transaction.atomic
    def save(self, request):
        user = super(CustomSignupForm, self).save(request)
        
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.save()
        
        # NOTA IMPORTANTE:
        # Esta lógica assume que o related_name de PerfilUsuario para User é 'perfil'.
        # Se você estiver usando o modelo 'UserProfile' do seu models.py anterior, o nome
        # de relacionamento padrão é 'userprofile', e você precisaria de 'user.userprofile.save()'.
        try:
             if hasattr(user, 'perfilusuario'): # Tentativa com o nome do modelo em minúsculo
                 perfil = user.perfilusuario
             elif hasattr(user, 'perfil'): # Tentativa com o related_name 'perfil'
                 perfil = user.perfil
             else:
                 # Se o signal post_save não criou o perfil ou o related_name é diferente
                 # Você pode precisar de UserProfile.objects.get_or_create(user=user)
                 perfil = PerfilUsuario.objects.get(user=user)

             perfil.tipoUsuario = 'Cliente'
             perfil.save()
        except Exception as e:
            # Em caso de erro na manipulação do perfil (ex: related_name errado ou perfil não criado)
            print(f"ATENÇÃO: Não foi possível salvar tipoUsuario no Perfil. Verifique o related_name da FK. Erro: {e}")
        
        return user