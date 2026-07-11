"""Утилиты безопасности: пути, редиректы, санитизация HTML."""
import os
import re

from django.utils.text import get_valid_filename

# Разрешённые расширения для медиа-библиотеки
ALLOWED_UPLOAD_EXTENSIONS = {
    # без .svg — в SVG можно встроить XSS
    '.jpg', '.jpeg', '.png', '.gif', '.webp',
    '.pdf', '.doc', '.docx', '.xls', '.xlsx', '.ppt', '.pptx',
    '.txt', '.csv', '.zip', '.rar', '.7z',
    '.mp4', '.webm', '.mp3', '.wav',
}

# Подкаталоги медиа (без path traversal)
ALLOWED_MEDIA_SUBDIRS = {
    'uploads', 'documents', 'banners', 'news', 'homepage',
    'programs', 'edu_programs', 'galleries', 'images',
}


def safe_join_media(media_root, *parts):
    """
    Безопасное соединение пути внутри MEDIA_ROOT.
    Блокирует .., абсолютные пути и выход за корень.
    """
    media_root = os.path.realpath(str(media_root))
    candidate = os.path.realpath(os.path.join(media_root, *[str(p) for p in parts]))
    if candidate != media_root and not candidate.startswith(media_root + os.sep):
        raise ValueError('Path escapes MEDIA_ROOT')
    return candidate


def sanitize_upload_subdir(subdir):
    """Только безопасное имя подкаталога."""
    raw = (subdir or 'uploads').strip()
    if raw.startswith(('/', '\\')) or (len(raw) > 1 and raw[1] == ':'):
        return 'uploads'
    subdir = raw.replace('\\', '/').strip('/')
    if not subdir or '..' in subdir or '/' in subdir or '\\' in subdir:
        return 'uploads'
    if subdir not in ALLOWED_MEDIA_SUBDIRS:
        # допускаем простой идентификатор
        if not re.fullmatch(r'[a-zA-Z0-9_-]{1,40}', subdir):
            return 'uploads'
    return subdir


def sanitize_upload_filename(name):
    """Безопасное имя файла + проверка расширения."""
    name = get_valid_filename(os.path.basename(name or 'file'))
    if not name or name in ('.', '..'):
        raise ValueError('Invalid filename')
    ext = os.path.splitext(name)[1].lower()
    if ext not in ALLOWED_UPLOAD_EXTENSIONS:
        raise ValueError(f'Extension not allowed: {ext}')
    return name


def is_safe_redirect_url(url, allowed_hosts, require_https=False):
    """Проверка next= от open redirect."""
    from django.utils.http import url_has_allowed_host_and_scheme
    if not url:
        return False
    return url_has_allowed_host_and_scheme(
        url,
        allowed_hosts=allowed_hosts,
        require_https=require_https,
    )


def sanitize_html(html):
    """
    Убирает опасные конструкции из HTML редактора (XSS).
    Оставляет разметку для CMS: таблицы, ссылки, изображения, списки.
    """
    if not html:
        return html
    try:
        import bleach
    except ImportError:
        # fallback без bleach: вырезать script/iframe/on*
        html = re.sub(r'(?is)<script[^>]*>.*?</script>', '', html)
        html = re.sub(r'(?is)<iframe[^>]*>.*?</iframe>', '', html)
        html = re.sub(r'(?is)<object[^>]*>.*?</object>', '', html)
        html = re.sub(r'(?is)<embed[^>]*>.*?</embed>', '', html)
        html = re.sub(r'(?i)\son\w+\s*=\s*("[^"]*"|\'[^\']*\'|[^\s>]+)', '', html)
        html = re.sub(r'(?i)javascript:', '', html)
        return html

    allowed_tags = [
        'p', 'br', 'hr', 'div', 'span', 'section',
        'h1', 'h2', 'h3', 'h4', 'h5', 'h6',
        'strong', 'em', 'b', 'i', 'u', 's', 'sub', 'sup',
        'ul', 'ol', 'li', 'blockquote', 'pre', 'code',
        'a', 'img', 'table', 'thead', 'tbody', 'tfoot', 'tr', 'th', 'td',
        'figure', 'figcaption', 'video', 'source', 'audio',
    ]
    allowed_attrs = {
        '*': ['class', 'id', 'title'],
        'a': ['href', 'target', 'rel', 'name'],
        'img': ['src', 'alt', 'width', 'height', 'loading'],
        'td': ['colspan', 'rowspan', 'width', 'height', 'style'],
        'th': ['colspan', 'rowspan', 'width', 'height', 'style'],
        'table': ['border', 'cellpadding', 'cellspacing', 'width', 'style'],
        'div': ['class', 'id', 'style', 'data-cms-table', 'contenteditable'],
        'span': ['class', 'id', 'style'],
        'p': ['class', 'id', 'style'],
        'video': ['src', 'controls', 'width', 'height'],
        'source': ['src', 'type'],
        'audio': ['src', 'controls'],
    }
    allowed_protocols = ['http', 'https', 'mailto', 'tel']
    css_sanitizer = None
    try:
        from bleach.css_sanitizer import CSSSanitizer
        css_sanitizer = CSSSanitizer(
            allowed_css_properties=[
                'color', 'background-color', 'background', 'font-size', 'font-weight',
                'font-style', 'text-align', 'text-decoration', 'width', 'height',
                'max-width', 'margin', 'padding', 'border', 'border-collapse',
                'vertical-align', 'display', 'float', 'clear',
            ]
        )
    except Exception:
        # без tinycss2 — не пропускаем style
        for key in list(allowed_attrs):
            attrs = [a for a in allowed_attrs[key] if a != 'style']
            allowed_attrs[key] = attrs

    return bleach.clean(
        html,
        tags=allowed_tags,
        attributes=allowed_attrs,
        protocols=allowed_protocols,
        strip=True,
        css_sanitizer=css_sanitizer,
    )
