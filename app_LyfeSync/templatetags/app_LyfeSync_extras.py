# app_LyfeSync/templatetags/app_LyfeSync_extras.py

from django import template
from django.core.serializers import serialize
import json
from django.utils.safestring import mark_safe

register = template.Library()

@register.filter
def get_item(dictionary, key):
    """Permite acessar um item de um dicionário por uma chave dinâmica no template."""
    return dictionary.get(key)

@register.filter
def jsonify(data):
    """Converte um objeto Python (incluindo QuerySets) em string JSON segura."""
    # Trata dados simples (dicionários, listas de tuplas)
    if isinstance(data, (dict, list)):
        return mark_safe(json.dumps(data))
    
    # Tenta serializar o objeto (útil para QuerySets, mas não necessário aqui)
    try:
        return mark_safe(serialize('json', data))
    except Exception:
        # Último recurso para strings simples ou outros tipos
        return mark_safe(json.dumps(str(data)))