from django import template
from django.utils.safestring import mark_safe

from cms.embed_utils import expand_content_embeds

register = template.Library()


@register.filter(is_safe=True)
def resolve_cms_embeds(value):
    if not value:
        return ''
    return mark_safe(expand_content_embeds(value))
