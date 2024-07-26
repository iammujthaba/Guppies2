from django import template

register = template.Library()

@register.filter
def strip_decimal(value):
    try:
        value = float(value)
        if value.is_integer():
            value = int(value)
    except (ValueError, TypeError):
        pass
    return value
