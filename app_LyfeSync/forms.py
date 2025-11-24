from django import forms
from .models import Habito, Gratidao, Afirmacao, Humor, Dicas, PerfilUsuario, HumorTipo
from django.utils import timezone
from django.forms import TextInput, DateInput, NumberInput, Select, Textarea, RadioSelect, HiddenInput, modelformset_factory
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserChangeForm, PasswordChangeForm
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from allauth.account.forms import SignupForm
from django.db import transaction
import re # Necessário para processar e limpar a descrição

User = get_user_model()

# -------------------------------------------------------------------
# FORMULÁRIO DE HÁBITO
# -------------------------------------------------------------------

class HabitoForm(forms.ModelForm):

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
#     Formulário GRATIDÃO (Criação de Múltiplos Registros)
# -------------------------------------------------------------------
class GratidaoCreateForm(forms.Form):
    """
    Formulário para registrar 3 gratidões de uma vez.
    """
    # Campo obrigatório para a data
    data = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-input w-full md:w-auto', 'required': 'required'}),
        label="Data da Gratidão"
    )

    # Campos para a primeira gratidão (apenas descrição)
    descricaogratidao_1 = forms.CharField(
        widget=forms.Textarea(attrs={'class': 'form-textarea resize-none', 'rows': 3, 'placeholder': 'Detalhe o motivo de sua gratidão...'}),
        label="Gratidão 1 (Descrição)",
        required=False
    )
    
    # Campos para a segunda gratidão (apenas descrição)
    descricaogratidao_2 = forms.CharField(
        widget=forms.Textarea(attrs={'class': 'form-textarea resize-none', 'rows': 3, 'placeholder': 'Detalhe o motivo de sua gratidão...'}),
        label="Gratidão 2 (Descrição)",
        required=False
    )

    # Campos para a terceira gratidão (apenas descrição)
    descricaogratidao_3 = forms.CharField(
        widget=forms.Textarea(attrs={'class': 'form-textarea resize-none', 'rows': 3, 'placeholder': 'Detalhe o motivo de sua gratidão...'}),
        label="Gratidão 3 (Descrição)",
        required=False
    )

    def generate_gratitude_name(self, description):
        """Gera o nome (título) da gratidão a partir da descrição, truncando se necessário."""
        if not description:
            return "Gratidão do Dia"
        
        # Pega a primeira linha da descrição
        first_line = description.split('\n')[0]
        name = first_line.strip()
        
        # Limpa espaços em excesso para garantir precisão no limite
        name = re.sub(r'\s+', ' ', name)
        
        # Limita a 100 caracteres
        if len(name) > 100:
             # Trunca a 97 caracteres e adiciona '...'
             name = name[:97].strip() + '...'
             
        return name if name else "Gratidão do Dia"


    def clean(self):
        """
        Garanti que pelo menos uma descrição de gratidão foi preenchida.
        (O problema "não deixa escrever" pode estar na view ou no template,
        mas o clean() aqui está correto para a regra de negócio.)
        """
        cleaned_data = super().clean()
        
        descriptions = [
            cleaned_data.get('descricaogratidao_1'),
            cleaned_data.get('descricaogratidao_2'),
            cleaned_data.get('descricaogratidao_3'),
        ]
        
        # Verifica se pelo menos uma descrição foi preenchida e não está vazia (após strip)
        filled_descriptions = [desc for desc in descriptions if desc and desc.strip()]
        
        if not filled_descriptions:
            raise ValidationError("Você deve preencher pelo menos uma das Descrições para registrar sua gratidão.")
        
        return cleaned_data

    def save(self, user):
        """
        Cria múltiplos objetos Gratidao em lote, usando bulk_create.
        """
        gratitude_objects = []
        data = self.cleaned_data['data']
        
        # O clean() já garantiu que pelo menos uma descrição está preenchida
        for i in range(1, 4):
            descricao = self.cleaned_data.get(f'descricaogratidao_{i}')
            
            if descricao and descricao.strip():
                # Gera o nome a partir da descrição
                nome = self.generate_gratitude_name(descricao)
                
                gratitude_objects.append(
                    Gratidao(
                        data=data,
                        descricaogratidao=descricao,
                        usuario=user
                    )
                )

        if not gratitude_objects:
            return [] # Retorna lista vazia se nada foi criado

        with transaction.atomic():
            # Cria todos os objetos de uma vez
            created_gratitudes = Gratidao.objects.bulk_create(gratitude_objects)
        
        return created_gratitudes


# --- Formulário para Alteração de uma única Gratidão ---
class GratidaoUpdateForm(forms.ModelForm):
    """
    Formulário para alterar uma única gratidão existente.
    """
    # Tornar a data read-only
    data = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-input w-full', 'required': 'required', 'readonly': 'readonly'}),
        label="Data da Gratidão"
    )
    

    descricaogratidao = forms.CharField(
        widget=forms.Textarea(attrs={'class': 'form-textarea resize-none', 'rows': 5}),
        label="Descrição Completa"
    )
    
    class Meta:
        model = Gratidao
        fields = ['data', 'descricaogratidao'] 
    
# -------------------------------------------------------------------
# FORMULÁRIO DE AFIRMAÇÃO
# -------------------------------------------------------------------

class AfirmacaoForm(forms.ModelForm):
    """
    Formulário para a criação de registros de Afirmação.
    """
    
    class Meta:
        model = Afirmacao
        fields = ['descricaoafirmacao'] # Mantemos apenas o campo principal para o Formset
        widgets = {
             # Removido o TextInput para o nome (título), focando no conteúdo
            'descricaoafirmacao': Textarea(attrs={
                'placeholder': 'Sua afirmação deve caber neste espaço...',
                'rows': 8,
                'class': 'form-control afirmacao-textarea bg-transparent border-0 text-dark p-4',
                'required': 'true'
            }),
             # 'data' e 'nomeafirmacao' serão definidos por fora ou no Formset para simplificar a UX
        }
        labels = {
            'descricaoafirmacao': 'Afirmação',
        }

# FORMSET DE AFIRMAÇÕES
# -------------------------------------------------------------------

AfirmacaoFormSet = modelformset_factory(
    Afirmacao,
    form=AfirmacaoForm,
    fields=('descricaoafirmacao',), # Apenas o campo de conteúdo para o registro
    extra=3, # Define que o formulário terá 3 instâncias
    max_num=3,
    can_delete=False # Desabilitamos a exclusão aqui, pois é para registro
)

# -------------------------------------------------------------------
# FORMULÁRIO DE HUMOR
# -------------------------------------------------------------------

class HumorForm(forms.ModelForm):
    """
    Formulário para a criação/edição de registros de Humor.
    
    """
    class Meta:
      model = Humor
      
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

# -------------------------------------------------------------------
# FORMULÁRIO DE DICAS
# -------------------------------------------------------------------

class DicasForm(forms.ModelForm):
    """
    Formulário para o administrador cadastrar novas dicas.
    Usa ModelChoiceField com RadioSelect para 'humor_relacionado'.
    """

    humor_relacionado = forms.ModelChoiceField(
        queryset=HumorTipo.objects.all(),
        widget=forms.RadioSelect(),
        required=True,
        label="Relacionar a qual Humor:",
        empty_label=None
    )

    class Meta:
      model = Dicas
      fields = ['humor_relacionado', 'nomeDica', 'descricaoDica', 'criado_por']
      
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
    
# -------------------------------------------------------------------
# Formulário de Atualização de Perfil (Nome e Sobrenome)
# -------------------------------------------------------------------
class UserUpdateForm(forms.ModelForm):
    """
    Formulário para o usuário editar seu nome e sobrenome.
    Utiliza ModelForm, que é mais limpo que UserChangeForm para esta finalidade.
    """
    class Meta:
        model = User
        fields = ['first_name', 'last_name']
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Aplica a classe 'form-control' do Bootstrap a todos os campos
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'

# -------------------------------------------------------------------
# Formulário de Perfil Estendido (tipoUsuario)
# -------------------------------------------------------------------
class PerfilUsuarioForm(forms.ModelForm):
    """
    Formulário para o usuário alterar o tipo de perfil.
    """
    class Meta:
        model = PerfilUsuario
        fields = ('tipoUsuario',)
        
        widgets = {
            # Note: Select é o widget base do Django. É melhor importá-lo.
            'tipoUsuario': Select(attrs={'class': 'form-select'}),
        }
        
    # O __init__ do PerfilUsuarioForm não precisa de nada extra por padrão

# -------------------------------------------------------------------
#Formulário de Alteração de Senha (NOVO - Segurança)
# -------------------------------------------------------------------
class CustomPasswordChangeForm(PasswordChangeForm):
    """
    Personaliza o PasswordChangeForm padrão do Django para aplicar
    classes Bootstrap 5 e labels em português.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Aplica a classe 'form-control' do Bootstrap a todos os campos
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'
            
        # Altera os labels dos campos para português
        self.fields['old_password'].label = 'Senha Atual'
        self.fields['new_password1'].label = 'Nova Senha'
        self.fields['new_password2'].label = 'Confirme a Nova Senha'
        
        # Remove a ajuda padrão do Django para a primeira nova senha, se existir.
        # Caso queira personalizar a mensagem de erro, use o help_text
        self.fields['new_password1'].help_text = None
        self.fields['new_password2'].help_text = None

# -------------------------------------------------------------------
# Formulário de Cadastro Customizado (Allauth)
# -------------------------------------------------------------------
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

# -------------------------------------------------------------------
#   Formulário de Consentimento para Dados e Privacidade
# -------------------------------------------------------------------
class ConsentimentoForm(forms.Form):
    """
    Formulário para o usuário confirmar que leu e concorda com
    os termos e políticas da plataforma.
    """
    # Campo booleano para aceitação. Required=True garante a validação.
    aceite_termos = forms.BooleanField(
        required=True,
        label="Li e concordo com os Termos de Uso e a Política de Privacidade da LyfeSync.",
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Remove o label automático para estilizar melhor no HTML, se desejar
        self.fields['aceite_termos'].label = False