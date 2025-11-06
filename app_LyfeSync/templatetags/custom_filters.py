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
