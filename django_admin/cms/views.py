from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.static import serve
from .models import Page, MenuItem, HomePage, Document, DocumentSection, Banner, News, EducationalProgram, AdmissionYear
import os


def _group_edu_by_year(page):
    """Группирует образовательные программы по годам: {year: [program, ...]}"""
    from collections import defaultdict
    result = defaultdict(list)

    programs = EducationalProgram.objects.filter(
        page=page, is_active=True
    ).prefetch_related('years__documents').order_by('order', 'code')

    for prog in programs:
        for yr in prog.years.filter(is_active=True).order_by('-year'):
            result[yr.year].append({
                'program': prog,
                'year_obj': yr,
                'docs': yr.documents.filter(is_active=True).order_by('order'),
            })

    # Сортируем по году убыванию
    return dict(sorted(result.items(), reverse=True))


def index(request):
    """Главная страница"""
    homepage = HomePage.load()
    menu_items = MenuItem.objects.filter(
    parent=None,
    is_active=True
).order_by('order', 'title')
    banners = Banner.objects.filter(is_active=True).order_by('order')
    latest_news = News.objects.filter(is_published=True)[:3]

    context = {
        'homepage': homepage,
        'menu_items': menu_items,
        'banners': banners,
        'latest_news': latest_news,
    }
    return render(request, 'cms/index.html', context)


def page_detail(request, slug):
    """Детальная страница"""
    page = get_object_or_404(Page, slug=slug, is_published=True)
    menu_items = MenuItem.objects.filter(
    parent=None,
    is_active=True
).order_by('order', 'title')
    
    # Получаем блоки контента
    content_blocks = page.blocks.filter(is_active=True).order_by('order')
    siblings = page.parent.subpages.filter(is_published=True).order_by('order', 'title') if page.parent else None
    children = page.subpages.filter(is_published=True).order_by('order', 'title')
    # Получаем документы по категориям с учётом порядка из DocumentSection
    documents_by_category = {}
    
    # Сначала получаем настроенный порядок разделов
    sections = {
        s.category: s
        for s in DocumentSection.objects.filter(page=page, is_active=True).order_by('order')
    }
    
    # Группируем документы по категориям
    raw_docs = {}
    for doc in page.documents.filter(is_active=True).order_by('category', 'order'):
        if doc.category not in raw_docs:
            raw_docs[doc.category] = []
        raw_docs[doc.category].append(doc)
    
    # Сначала добавляем категории в порядке из DocumentSection
    for cat, section in sorted(sections.items(), key=lambda x: x[1].order):
        if cat in raw_docs:
            documents_by_category[cat] = {'title': section.title, 'docs': raw_docs[cat]}
    
    # Затем добавляем оставшиеся категории (без настроенного порядка)
    for cat, docs in raw_docs.items():
        if cat not in documents_by_category:
            # Используем display-название из первого документа
            documents_by_category[cat] = {'title': docs[0].get_category_display(), 'docs': docs}
    
    context = {
    'page': page,
    'menu_items': menu_items,
    'content_blocks': content_blocks,
    'documents_by_category': documents_by_category,
    'siblings': siblings,
    'children': children,
    'edu_programs': EducationalProgram.objects.filter(
        page=page, is_active=True
    ).prefetch_related(
        'years__documents'
    ).order_by('order', 'code'),
    'edu_by_year': _group_edu_by_year(page),
}
    return render(request, 'cms/page_detail.html', context)


def news_list(request):
    """Страница новостей"""
    menu_items = MenuItem.objects.filter(
    parent=None,
    is_active=True
).order_by('order', 'title')
    news = News.objects.filter(is_published=True)
    context = {
        'news': news,
        'menu_items': menu_items,
    }
    return render(request, 'cms/news_list.html', context)


def news_detail(request, slug):
    """Детальная новость"""
    news_item = get_object_or_404(News, slug=slug, is_published=True)
    menu_items = MenuItem.objects.filter(
    parent=None,
    is_active=True
).order_by('order', 'title')
    recent = News.objects.filter(is_published=True).exclude(slug=slug)[:4]
    context = {
        'news_item': news_item,
        'menu_items': menu_items,
        'recent': recent,
    }
    return render(request, 'cms/news_detail.html', context)


@csrf_exempt
def api_menu(request):
    menu_items = MenuItem.objects.filter(parent=None, is_active=True).order_by('order', 'title')

    def serialize_menu_item(item):
        return {
            'id': item.id,
            'title': item.title,
            'url': item.get_absolute_url(),
            'children': [
                serialize_menu_item(child)
                for child in item.get_children().filter(is_active=True).order_by('order', 'title')
            ]
        }

    data = [serialize_menu_item(item) for item in menu_items]
    return JsonResponse(data, safe=False)


@csrf_exempt
def api_homepage(request):
    """API для получения данных главной страницы"""
    homepage = HomePage.load()
    
    data = {
        'welcome_title': homepage.welcome_title,
        'welcome_text': homepage.welcome_text,
        'director_name': homepage.director_name,
        'director_position': homepage.director_position,
        'director_image': homepage.director_image.url if homepage.director_image else '',
        'director_message': homepage.director_message,
        'slider_title': homepage.slider_title,
        'slider_text': homepage.slider_text,
        'slider_image': homepage.slider_image.url if homepage.slider_image else '',
    }
    return JsonResponse(data)


@csrf_exempt
def api_page(request, slug):
    """API для получения данных страницы"""
    page = get_object_or_404(Page, slug=slug, is_published=True)
    
    blocks = []
    for block in page.blocks.filter(is_active=True).order_by('order'):
        blocks.append({
            'id': block.id,
            'type': block.block_type,
            'title': block.title,
            'content': block.content,
            'order': block.order,
        })
    
    documents = []
    for doc in page.documents.filter(is_active=True).order_by('category', 'order'):
        documents.append({
            'id': doc.id,
            'category': doc.category,
            'category_display': doc.get_category_display(),
            'title': doc.title,
            'description': doc.description,
            'file_url': doc.file.url if doc.file and doc.file.name else '',
            'file_size': doc.file_size,
        })
    
    data = {
        'id': page.id,
        'title': page.title,
        'slug': page.slug,
        'description': page.description,
        'content': page.content,
        'blocks': blocks,
        'documents': documents,
    }
    return JsonResponse(data)


def search(request):
    """Поиск по сайту"""
    from django.db.models import Q
    query = request.GET.get('q', '').strip()
    menu_items = MenuItem.objects.filter(
    parent=None,
    is_active=True
).order_by('order', 'title')

    pages = []
    documents = []
    news_results = []

    if query:
        # Поиск по страницам
        pages = Page.objects.filter(
            is_published=True
        ).filter(
            Q(title__icontains=query) |
            Q(description__icontains=query) |
            Q(content__icontains=query)
        ).distinct()

        # Поиск по документам
        documents = Document.objects.filter(
            is_active=True
        ).filter(
            Q(title__icontains=query) |
            Q(description__icontains=query)
        ).select_related('page').distinct()

        # Поиск по новостям
        try:
            from .models import News
            news_results = News.objects.filter(
                is_published=True
            ).filter(
                Q(title__icontains=query) |
                Q(content__icontains=query)
            ).distinct()
        except Exception:
            pass

    context = {
        'query': query,
        'pages': pages,
        'documents': documents,
        'news_results': news_results,
        'total': len(list(pages)) + len(list(documents)) + len(list(news_results)),
        'menu_items': menu_items,
    }
    return render(request, 'cms/search.html', context)
