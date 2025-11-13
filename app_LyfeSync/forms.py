# forms.py
from django import forms
from .models import Habito, Gratidao, Afirmacao, Humor, Dicas, PerfilUsuario, HumorTipo
from django.utils import timezone
from django.forms import TextInput, DateInput, NumberInput, Select, Textarea, RadioSelect, HiddenInput
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserChangeForm
from django.contrib.auth.models import User
from allauth.account.forms import SignupForm
from django.db import transaction

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
         # Esta linha exige que Habito.FREQUENCIA_CHOICES exista no modelo
         'frequencia': Select(
            choices=Habito.FREQUENCIA_CHOICES, 
            attrs={'class': 'form-select'} 
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
   
   IMPORTANTE: O campo 'idusuario' foi removido de fields, pois é preenchido
   programaticamente na view e não deve ser validado pelo POST.
   """
   class Meta:
      model = Humor
      
      # CORREÇÃO: Removido 'idusuario' desta lista
      fields = ('estado', 'descricaohumor', 'data') 
      
      widgets = {
         # O campo 'estado' usa Select por ser FK (embora seja substituído por JS no template)
         'estado': Select(attrs={ 
            'class': 'form-select', 
         }),
         'descricaohumor': Textarea(attrs={ 
            'class': 'form-control',
            'rows': 3,
            'placeholder': 'Detalhe o motivo do seu humor...'
         }),
         'data': DateInput(attrs={
            'class': 'form-control',
            'type': 'date'
         }),
         # 'idusuario' removido
      }
      
      labels = {
         'estado': 'Qual o seu humor?',
         'descricaohumor': 'Detalhes/Motivação',
         'data': 'Data do Registro',
         # 'idusuario' label removido
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
   Formulário para o administrador cadastrar novas dicas.
   Usa ModelChoiceField com RadioSelect para 'humor_relacionado'.
   """
   # CORREÇÃO PRINCIPAL: Garante que o campo FK seja ModelChoiceField com RadioSelect
   # O campo 'humor_relacionado' deve corresponder ao nome do campo FK no modelo Dicas
   humor_relacionado = forms.ModelChoiceField(
      queryset=HumorTipo.objects.all(),
      # O widget RadioSelect permite estilizar melhor a seleção no template
      widget=forms.RadioSelect(), 
      required=True, 
      label="Relacionar a qual Humor:",
      empty_label=None
   )

   class Meta:
      model = Dicas 
      # CORRIGIDO: Garante que 'humor_relacionado' e 'criado_por' estão nos fields, se aplicável
      # Assumindo que 'criado_por' é preenchido na view, mantemos ele como Hidden.
      fields = ['humor_relacionado', 'nomeDica', 'descricaoDica', 'criado_por'] # Adicionado 'criado_por'
      
      widgets = {
         'nomeDica': TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Digite um título curto para a dica'
         }),
         'descricaoDica': Textarea(attrs={
            'class': 'form-control',
            'rows': 5, 
            'placeholder': 'Escreva aqui a descrição detalhada da dica...',
            'style': 'min-height: 200px;'
         }),
         # Adicionado widget para 'criado_por' (assumindo que existe no modelo Dicas)
         'criado_por': HiddenInput(), 
      }

   # Removemos o __init__ customizado para aplicação de classes, pois os widgets
   # já definem a classe 'form-control' corretamente e o ModelChoiceField é customizado.
   
# -------------------------------------------------------------------
# 3. FORMULÁRIOS DE USUÁRIO E PERFIL
# -------------------------------------------------------------------

class UserUpdateForm(UserChangeForm):
   """
   Formulário para o usuário editar seu nome e sobrenome.
   """
   class Meta:
      model = User
      fields = ('first_name', 'last_name') 
      
      widgets = {
         'first_name': TextInput(attrs={'class': 'form-control'}),
         'last_name': TextInput(attrs={'class': 'form-control'}),
      }

   def __init__(self, *args, **kwargs):
        super(UserUpdateForm, self).__init__(*args, **kwargs)
        if 'password' in self.fields:
            # Garante que o campo 'password' é removido
            del self.fields['password'] 
        
        # Aplica a classe de estilo Bootstrap no init para garantir consistência
        for field in self.fields.values():field.widget.attrs.update({'class': 'form-control'})

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
      pass

class CustomSignupForm(SignupForm):
   """
   Formulário de cadastro customizado para incluir nome e sobrenome no User.
   Integrado com allauth.
   """
   # Estes campos serão incluídos no formulário de cadastro do allauth
   first_name = forms.CharField(max_length=150, label='Nome', widget=TextInput(attrs={'class': 'form-control'}))
   last_name = forms.CharField(max_length=150, label='Sobrenome', widget=TextInput(attrs={'class': 'form-control'}))

   @transaction.atomic
   def save(self, request):
      
      # 1. Chama o save original (cria o objeto User, mas sem nome/sobrenome ainda)
      user = super(CustomSignupForm, self).save(request)
      
      # 2. Atualiza os campos extras
      user.first_name = self.cleaned_data['first_name']
      user.last_name = self.cleaned_data['last_name']
      
      # 3. Salva o User
      user.save()
      
      # 4. Configura o PerfilUsuario (Assumindo que o sinal já o criou)
      if hasattr(user, 'perfil'):
        user.perfil.tipoUsuario = 'Cliente'
        user.perfil.save()
      
      return user