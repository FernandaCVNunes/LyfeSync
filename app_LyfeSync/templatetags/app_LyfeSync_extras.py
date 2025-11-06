# app_LyfeSync/templatetags/app_LyfeSync_extras.py

from django import template

register = template.Library()

@register.filter
def get_item(dictionary, key):
    """Permite acessar um item de um dicionário por uma chave dinâmica no template."""
    return dictionary.get(key)