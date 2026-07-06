from django.db.models import Max

from .models import MenuItem, HomeQuickLink


def sync_page_to_menu(page):
    """Создаёт или обновляет пункт меню, если у страницы включено «Показывать в меню»."""
    if not page.show_in_menu:
        return None

    parent_item = None
    if page.parent_id:
        parent_item = MenuItem.objects.filter(page=page.parent).first()
        if not parent_item:
            parent_item = MenuItem.objects.filter(slug=page.parent.slug).first()

    mi, _ = MenuItem.objects.update_or_create(
        page=page,
        defaults={
            'title': page.title,
            'slug': page.slug,
            'parent': parent_item,
            'order': page.order,
            'is_active': page.is_published,
        },
    )
    return mi


def next_quicklink_order():
    current = HomeQuickLink.objects.aggregate(m=Max('order'))['m']
    return (current or 0) + 1


def free_quicklink_style():
    """Первый свободный стиль для новой плитки."""
    used = set(HomeQuickLink.objects.values_list('style', flat=True))
    for style, _ in HomeQuickLink.STYLE_CHOICES:
        if style not in used:
            return style
    return 'bento-g7'
