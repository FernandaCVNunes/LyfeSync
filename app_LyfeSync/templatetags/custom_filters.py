from django import template
from django.template.defaultfilters import stringfilter

register = template.Library()

@register.filter
@stringfilter
def split(value, arg):
    """
    Divide o valor (string) pelo argumento (separador).
    Uso: {{ value|split:"," }}
    """
    return value.split(arg)

@register.filter(name='split_by_space')
def split_by_space(value):
    """
    Divide uma string por espaços e retorna a lista de strings.
    Geralmente usado para pegar a primeira palavra.
    Exemplo: "Muito Feliz" | split_by_space -> ['Muito', 'Feliz']
    """
    if not isinstance(value, str):
        return value
    return value.split(' ')

@register.filter(name='first_word')
def first_word(value):
    """
    Retorna apenas a primeira palavra de uma string.
    """
    if not isinstance(value, str):
        return value
    return value.split(' ')[0]

@register.filter(name='get_item') 
def get_item(dictionary, key):
    """Permite acessar o valor de um dicionário usando uma variável como chave."""
    return dictionary.get(key)