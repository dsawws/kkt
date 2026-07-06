"""Поиск без учёта регистра (SQLite плохо ищет кириллицу через icontains)."""


def _match(query, *values):
    q = query.lower()
    for val in values:
        if val and q in str(val).lower():
            return True
    return False


def search_pages(queryset, query):
    query = query.strip()
    if not query:
        return queryset.none()
    ids = [
        obj.pk for obj in queryset
        if _match(query, obj.title, obj.description, obj.content, obj.slug)
    ]
    return queryset.filter(pk__in=ids)


def search_documents(queryset, query):
    query = query.strip()
    if not query:
        return queryset.none()
    ids = [
        obj.pk for obj in queryset.select_related('page')
        if _match(query, obj.title, obj.description, obj.page.title if obj.page else '')
    ]
    return queryset.filter(pk__in=ids)


def search_news(queryset, query):
    query = query.strip()
    if not query:
        return queryset.none()
    ids = [
        obj.pk for obj in queryset
        if _match(query, obj.title, obj.excerpt, obj.content, obj.slug)
    ]
    return queryset.filter(pk__in=ids)
