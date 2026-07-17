from .models import HomePage, MenuItem


def _dedupe_root_menu(items):
    """Убирает дубликаты корневых пунктов с одинаковым названием.
    Предпочитает пункт со связанной страницей и с большим числом детей.
    """
    items = list(items)
    best = {}
    for item in items:
        key = (item.title or '').strip().casefold()
        if not key:
            continue
        children = item.get_children().filter(is_active=True).count()
        score = (1 if item.page_id else 0, children, -item.order, item.pk)
        prev = best.get(key)
        if prev is None or score > prev[1]:
            best[key] = (item.pk, score)
    keep = {pk for pk, _ in best.values()}
    return [item for item in items if item.pk in keep]


def get_root_menu_items():
    menu_items = MenuItem.objects.filter(
        parent=None, is_active=True
    ).order_by('order', 'title')
    return _dedupe_root_menu(menu_items)


def site_context(request):
    homepage = HomePage.load()
    return {
        'site_settings': homepage,
        'menu_items': get_root_menu_items(),
    }
