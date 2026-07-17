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

    # Не плодить дубликаты: сначала по page, иначе по slug без page
    mi = MenuItem.objects.filter(page=page).first()
    if not mi:
        mi = MenuItem.objects.filter(page__isnull=True, slug=page.slug).first()
    if not mi:
        mi = MenuItem(page=page)

    mi.page = page
    mi.title = page.title
    mi.slug = page.slug
    mi.parent = parent_item
    mi.order = page.order
    mi.is_active = page.is_published
    mi.save()

    # Деактивируем «сиротские» корни с тем же названием без привязки к page
    if parent_item is None:
        MenuItem.objects.filter(
            parent=None,
            title=page.title,
            is_active=True,
        ).exclude(pk=mi.pk).update(is_active=False)

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
