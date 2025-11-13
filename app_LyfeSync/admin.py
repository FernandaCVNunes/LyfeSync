# app_LyfeSync/admin.py
from django.contrib import admin
# Importando todos os modelos do selfcare_models.py para registro no Admin
from .models import Humor, HumorTipo, Gratidao, Afirmacao, Dicas, Habito


# ===================================================================
# REGISTRO: HUMORTIPO
# ===================================================================

@admin.register(HumorTipo)
class HumorTipoAdmin(admin.ModelAdmin):
    """
    Configuração do painel Admin para o modelo HumorTipo.
    """
    # Usando 'pk' para a chave primária
    list_display = ('pk', 'estado', 'icone')
    search_fields = ('estado',)

# ===================================================================
# REGISTRO: HUMOR
# ===================================================================

@admin.register(Humor)
class HumorAdmin(admin.ModelAdmin):
    
    # Campos exibidos na tela de listagem de registros
    list_display = ('usuario', 'data', 'estado', 'descricaohumor', 'data_registro')
    
    # Campos que permitem a filtragem lateral
    list_filter = ('estado', 'data')
    
    # Permite pesquisar por descrição do humor e pelo username do usuário
    search_fields = ('descricaohumor', 'usuario__username') 
    
    # Garante que o usuário seja apenas preenchido ou visualizado, mas não editado
    readonly_fields = ('usuario', 'data_registro')
    
    # Define os campos no formulário de edição do Admin
    fieldsets = (
        (None, {'fields': ('usuario', 'data', 'estado')}),
        ('Detalhes', {'fields': ('descricaohumor', 'data_registro')}),
    )

# ===================================================================
# REGISTRO: GRATIDÃO
# ===================================================================

@admin.register(Gratidao)
class GratidaoAdmin(admin.ModelAdmin):
    # CORREÇÃO DEFINITIVA: Usando 'descricaogratidao' (tudo minúsculo) e 'data' (não existe data_registro)
    list_display = ('idgratidao', 'usuario', 'data', 'nomegratidao', 'descricaogratidao')
    list_filter = ('data',)
    # Usando 'descricaogratidao' na busca.
    search_fields = ('descricaogratidao', 'usuario__username') 

# ===================================================================
# REGISTRO: AFIRMAÇÃO
# ===================================================================

@admin.register(Afirmacao)
class AfirmacaoAdmin(admin.ModelAdmin):
    # CORREÇÃO DEFINITIVA: Usando 'descricaoafirmacao' e 'data' (não existe data_registro)
    list_display = ('idafirmacao', 'usuario', 'data', 'nomeafirmacao', 'descricaoafirmacao')
    list_filter = ('data',)
    # Usando 'descricaoafirmacao' na busca.
    search_fields = ('descricaoafirmacao', 'usuario__username')

# ===================================================================
# REGISTRO: HÁBITO
# ===================================================================

@admin.register(Habito)
class HabitoAdmin(admin.ModelAdmin):
    # Assumindo que o campo do usuário agora se chama 'usuario'
    list_display = ('nome', 'usuario', 'data_inicio', 'frequencia', 'quantidade')
    list_filter = ('frequencia',)
    search_fields = ('nome', 'usuario__username')

# ===================================================================
# REGISTRO: DICAS
# ===================================================================

@admin.register(Dicas)
class DicasAdmin(admin.ModelAdmin):
    # Usando os campos fornecidos. Mantendo data_criacao, que existe no modelo Dicas.
    list_display = ('idDica', 'nomeDica', 'humor_relacionado', 'data_criacao', 'criado_por')
    list_filter = ('humor_relacionado',)
    # Usando 'descricaoDica' como campo de busca.
    search_fields = ('nomeDica', 'descricaoDica', 'criado_por__username')