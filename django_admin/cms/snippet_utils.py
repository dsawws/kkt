"""HTML-сниппеты для вставки в редактор страниц."""
from django.utils.html import escape


def document_snippet_html(doc):
    """Блок загрузки документа (как на сайте)."""
    if doc.external_url:
        url = doc.external_url
        btn_icon = 'fa-external-link-alt'
        btn_text = 'Открыть'
    elif doc.file and doc.file.name:
        url = doc.file.url
        btn_icon = 'fa-download'
        btn_text = 'Скачать'
    else:
        url = ''
        btn_icon = 'fa-clock'
        btn_text = 'Скоро'

    title = escape(doc.title)
    desc = f'<p>{escape(doc.description)}</p>' if doc.description else ''
    size = f'<p>{escape(doc.file_size)}</p>' if doc.file_size else ''

    if url:
        btn = (
            f'<a href="{url}" class="download-btn" target="_blank" rel="noopener">'
            f'<i class="fas {btn_icon}"></i> {btn_text}</a>'
        )
    else:
        btn = (
            f'<span class="download-btn" style="background:#9e9e9e;cursor:default;">'
            f'<i class="fas {btn_icon}"></i> {btn_text}</span>'
        )

    return (
        '<div class="document-item">'
        '<div class="document-icon"><i class="fas fa-file-pdf"></i></div>'
        f'<div class="document-info"><h3>{title}</h3>{desc}{size}</div>'
        f'{btn}'
        '</div>'
    )
