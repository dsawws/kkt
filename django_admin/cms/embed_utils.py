"""Встраивание переиспользуемых сущностей (таблицы) в контент страниц."""
import re

from django.utils.html import escape

TABLE_EMBED_RE = re.compile(r'\[\[cms-table:([^\]]+)\]\]')
TABLE_EMBED_DIV_RE = re.compile(
    r'<div[^>]*\bcms-embed-table\b[^>]*\bdata-cms-table="([^"]+)"[^>]*>.*?</div>',
    re.IGNORECASE | re.DOTALL,
)
TABLE_EMBED_DIV_RE_ALT = re.compile(
    r'<div[^>]*\bdata-cms-table="([^"]+)"[^>]*\bcms-embed-table\b[^>]*>.*?</div>',
    re.IGNORECASE | re.DOTALL,
)


def table_embed_tag(slug):
    return f'[[cms-table:{slug}]]'


def table_embed_placeholder_html(slug, title):
    """Визуальный блок в редакторе (в БД сохраняется как shortcode)."""
    title = escape(title or slug)
    slug = escape(slug)
    return (
        f'<div class="cms-embed-table" data-cms-table="{slug}" contenteditable="false">'
        f'<span class="cms-embed-table__icon">&#128202;</span> '
        f'<span class="cms-embed-table__label">Таблица: <strong>{title}</strong></span> '
        f'<span class="cms-embed-table__hint">— переиспользуемый блок, редактируется в «Таблицы»</span>'
        f'</div>'
    )


def normalize_content_embeds(html):
    """Перед сохранением: placeholder div → shortcode."""
    if not html:
        return html

    def div_to_tag(match):
        return table_embed_tag(match.group(1).strip())

    html = TABLE_EMBED_DIV_RE.sub(div_to_tag, html)
    html = TABLE_EMBED_DIV_RE_ALT.sub(div_to_tag, html)
    return html


def expand_content_embeds(html):
    """При отображении: shortcode и legacy div → актуальное содержимое таблицы."""
    if not html:
        return html

    from .models import ContentTable

    cache = {}

    def lookup(key):
        key = key.strip()
        if key in cache:
            return cache[key]
        table = ContentTable.objects.filter(slug=key).first()
        if not table and key.isdigit():
            table = ContentTable.objects.filter(pk=int(key)).first()
        cache[key] = table
        return table

    def replace(match):
        table = lookup(match.group(1))
        if table:
            return table.content
        return match.group(0)

    html = TABLE_EMBED_RE.sub(replace, html)
    html = TABLE_EMBED_DIV_RE.sub(replace, html)
    html = TABLE_EMBED_DIV_RE_ALT.sub(replace, html)
    return html


def content_for_editor(html):
    """Shortcode → placeholder для CKEditor."""
    if not html:
        return html

    from .models import ContentTable

    def replace(match):
        key = match.group(1).strip()
        table = ContentTable.objects.filter(slug=key).first()
        if not table and key.isdigit():
            table = ContentTable.objects.filter(pk=int(key)).first()
        title = table.title if table else key
        return table_embed_placeholder_html(key, title)

    return TABLE_EMBED_RE.sub(replace, html)


def find_pages_using_table(table):
    """Страницы, где вставлена таблица."""
    from .models import Page

    tag = table_embed_tag(table.slug)
    div_key = f'data-cms-table="{table.slug}"'
    result = []
    for page in Page.objects.only('id', 'title', 'slug', 'content'):
        content = page.content or ''
        if tag in content or div_key in content:
            result.append(page)
    return result
