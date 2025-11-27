from django import template

register = template.Library()

@register.filter
def split(value, separator=','):
    """Divide un string en lista usando un separador. Devuelve lista limpia."""
    if not value:
        return []
    return [item.strip() for item in value.split(separator)]

@register.filter
def trim(value):
    """Elimina espacios al inicio/fin."""
    if not value:
        return ''
    return value.strip()

@register.filter
def dict_get(dict_obj, key):
    """Obtiene dinámicamente dict[key] en templates."""
    if isinstance(dict_obj, dict):
        return dict_obj.get(key)
    return None
