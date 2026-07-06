from django import template

register = template.Library()


@register.filter
def get_attr(obj, attr):
    val = getattr(obj, attr, None)
    if val is None:
        return ''
    if isinstance(val, (str, int, float, bool)):
        return val
    if hasattr(val, 'get_block_type_display'):
        return val.get_block_type_display()
    if hasattr(val, 'get_doc_type_display'):
        return val.get_doc_type_display()
    if hasattr(val, 'title'):
        return val.title
    return str(val)
