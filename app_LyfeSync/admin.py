# app_LyfeSync/admin.py
from django.contrib import admin
from .models import Humor, HumorTipo 
# Se tiver outros modelos do selfcare_models.py, importe-os aqui também:
# from .models import Habito, StatusDiario, Afirmacao, Gratidao, Dicas, Relatorio


# REGISTRO PARA O MODELO HUMORTIPO
@admin.register(HumorTipo)
class HumorTipoAdmin(admin.ModelAdmin):
    """
    Configuração do painel Admin para o modelo HumorTipo.
    """
    # Adicionando 'icone' para facilitar a visualização no Admin
    list_display = ('id_tipo_humor', 'estado', 'icone')
    search_fields = ('estado',)

# REGISTRO PARA O MODELO HUMOR (Corrigido com 'estado')
@admin.register(Humor)
class HumorAdmin(admin.ModelAdmin):
    """
    CORRIGIDO: O campo 'idHumor' foi substituído pelo nome correto do campo no 
    modelo Humor, que é 'estado'.
    """
    
    # Campos exibidos na tela de listagem de registros
    # O campo 'estado' agora refere-se corretamente à ForeignKey para HumorTipo
    list_display = ('idusuario', 'data', 'estado', 'descricaohumor', 'data_registro')
    
    # Campos que permitem a filtragem lateral
    list_filter = ('estado', 'data')
    
    # Permite pesquisar por descrição do humor e pelo username do usuário
    search_fields = ('descricaohumor', 'idusuario__username') 
    
    # Garante que o usuário seja apenas preenchido ou visualizado, mas não editado
    readonly_fields = ('idusuario', 'data_registro')
    
    # Define os campos no formulário de edição do Admin
    fieldsets = (
        (None, {'fields': ('idusuario', 'data', 'estado')}), # 'estado' aqui
        ('Detalhes', {'fields': ('descricaohumor', 'data_registro')}),
    )

# Se desejar registrar os outros modelos do seu models.py, você pode adicionar:
# @admin.register(Habito)
# class HabitoAdmin(admin.ModelAdmin):
#     list_display = ('nome', 'usuario', 'data_inicio', 'frequencia', 'quantidade')
#     list_filter = ('frequencia',)
#     search_fields = ('nome', 'usuario__username')

# @admin.register(Dicas)
# class DicasAdmin(admin.ModelAdmin):
#     list_display = ('nomeDica', 'humor_relacionado', 'data_criacao', 'criado_por')
#     list_filter = ('humor_relacionado',)
#     search_fields = ('nomeDica', 'descricaoDica')