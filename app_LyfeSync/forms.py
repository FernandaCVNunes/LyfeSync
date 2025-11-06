from django import forms
# A importação do modelo Dicas já está correta
from .models import Habito, Gratidao, Afirmacao, Humor, Dicas, PerfilUsuario
from django.utils import timezone
from django.forms import ModelForm, TextInput, DateInput, NumberInput, Select, Textarea
from django.contrib.auth.forms import UserChangeForm
from django.contrib.auth.models import User

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
                # ALTERAÇÃO: Usando timezone.localdate() é mais seguro para campos DateField
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
# 2. FORMULÁRIOS PARA AUTOCUIDADO (IMPLEMENTADOS)
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
            # O campo 'estado' se beneficia de um Select com as choices definidas no Model
            'estado': Select(attrs={'class': 'form-control'}), 
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

class DicasForm(forms.ModelForm): # NOME SUGERIDO CORRIGIDO PARA 'DicasForm'
    """
    Formulário para o administrador cadastrar novas dicas de humor.
    """
    
    class Meta:
        model = Dicas  # <--- CORREÇÃO CRÍTICA AQUI! Deve ser 'Dicas'.
        fields = ['TipoHumor', 'nomeDica', 'descricaoDica'] # CORRIGIDO: Campos para corresponder ao models.py
        
        widgets = {
            # ALTERAÇÃO: Padronizando o uso de 'form-control' para consistência
            'TipoHumor': forms.Select(attrs={
                'class': 'form-control' 
            }),
            'nomeDica': forms.TextInput(attrs={ # CORRIGIDO: nomeDica
                'class': 'form-control',
                'placeholder': 'Digite um título curto para a dica'
            }),
            'descricaoDica': forms.Textarea(attrs={ # CORRIGIDO: descricaoDica
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
    Formulário para o usuário editar seu nome e sobrenome.
    """
    class Meta:
        model = User
        fields = ('first_name', 'last_name') # Campos que o cliente pode editar
        
        # ADICIONADO: Widgets para aplicar o estilo Bootstrap
        widgets = {
            'first_name': TextInput(attrs={'class': 'form-control'}),
            'last_name': TextInput(attrs={'class': 'form-control'}),
        }


    # Removemos o campo 'password' para evitar que o cliente altere a senha acidentalmente
    def __init__(self, *args, **kwargs):
        super(UserUpdateForm, self).__init__(*args, **kwargs)
        if 'password' in self.fields:
            # Garante que o campo 'password' é removido
            del self.fields['password'] 
        
        # ADICIONADO: Aplica a classe de estilo Bootstrap no init também para garantir
        for field in self.fields.values():
             field.widget.attrs.update({'class': 'form-control'})
             
# Formulário para o Perfil (Contém tipoUsuario)
class PerfilUsuarioForm(forms.ModelForm):
    """
    Formulário para o usuário alterar o tipo de perfil (Ex: Básico, Premium).
    """
    class Meta:
        model = PerfilUsuario
        fields = ('tipoUsuario',) # O campo que queremos mostrar e editar
        
        # ALTERAÇÃO: Movido a definição de widget para a classe Meta, seguindo o padrão
        widgets = {
             'tipoUsuario': Select(attrs={'class': 'form-select'}),
        }
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        pass