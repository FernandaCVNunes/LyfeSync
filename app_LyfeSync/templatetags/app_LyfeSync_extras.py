# app_LyfeSync/templatetags/app_LyfeSync_extras.py

from django import template
from django.core.serializers import serialize
import json
from django.utils.safestring import mark_safe

register = template.Library()

@register.filter
def get_item(dictionary, key):
    """
    Permite acessar um item de um dicionário por uma chave dinâmica no template.
    
    Adicionado tratamento para evitar 'AttributeError: 'str' object has no attribute 'get''
    caso 'dictionary' seja uma string ou outro tipo não-dicionário.
    """
    # Verifica se o objeto 'dictionary' possui o método 'get'.
    # Isso cobre dicionários, QueryDicts (como request.POST/GET) e outros objetos
    # semelhantes a dicionários, evitando a falha se for uma string (str).
    if hasattr(dictionary, 'get'):
        return dictionary.get(key)
    # Se o objeto não suportar .get() (ex: é uma string, None, etc.),
    # retorna None de forma segura.
    return None

@register.filter
def jsonify(data):
    """Converte um objeto Python (incluindo QuerySets) em string JSON segura."""
    # Trata dados simples (dicionários, listas de tuplas)
    if isinstance(data, (dict, list)):
        return mark_safe(json.dumps(data))
    
    # Tenta serializar o objeto (útil para QuerySets)
    try:
        return mark_safe(serialize('json', data))
    except Exception:
        # Último recurso para strings simples ou outros tipos, garantindo
        # que o retorno sempre seja uma string JSON válida.
        return mark_safe(json.dumps(str(data)))