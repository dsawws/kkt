from .models import HomePage, MenuItem


def site_context(request):
    homepage = HomePage.load()
    menu_items = MenuItem.objects.filter(
        parent=None, is_active=True
    ).order_by('order', 'title')
    return {
        'site_settings': homepage,
        'menu_items': menu_items,
    }
