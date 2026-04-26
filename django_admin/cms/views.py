from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.static import serve
from .models import Page, MenuItem, HomePage, Document, Banner, News
import os


def index(request):
    """Главная страница"""
    homepage = HomePage.load()
    menu_items = MenuItem.objects.filter(parent=None, is_active=True).prefetch_related('children')
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
    menu_items = MenuItem.objects.filter(parent=None, is_active=True).prefetch_related('children')
    
    # Получаем блоки контента
    content_blocks = page.blocks.filter(is_active=True).order_by('order')
    
    # Получаем документы по категориям (только с файлами или без — показываем все)
    documents_by_category = {}
    for doc in page.documents.filter(is_active=True).order_by('category', 'order'):
        if doc.category not in documents_by_category:
            documents_by_category[doc.category] = []
        documents_by_category[doc.category].append(doc)
    
    context = {
        'page': page,
        'menu_items': menu_items,
        'content_blocks': content_blocks,
        'documents_by_category': documents_by_category,
    }
    return render(request, 'cms/page_detail.html', context)


def news_list(request):
    """Страница новостей"""
    menu_items = MenuItem.objects.filter(parent=None, is_active=True).prefetch_related('children')
    news = News.objects.filter(is_published=True)
    context = {
        'news': news,
        'menu_items': menu_items,
    }
    return render(request, 'cms/news_list.html', context)


def news_detail(request, slug):
    """Детальная новость"""
    news_item = get_object_or_404(News, slug=slug, is_published=True)
    menu_items = MenuItem.objects.filter(parent=None, is_active=True).prefetch_related('children')
    recent = News.objects.filter(is_published=True).exclude(slug=slug)[:4]
    context = {
        'news_item': news_item,
        'menu_items': menu_items,
        'recent': recent,
    }
    return render(request, 'cms/news_detail.html', context)


@csrf_exempt
def api_menu(request):
    """API для получения меню"""
    menu_items = MenuItem.objects.filter(parent=None, is_active=True).prefetch_related('children')
    
    def serialize_menu_item(item):
        return {
            'id': item.id,
            'title': item.title,
            'url': item.get_absolute_url(),
            'children': [serialize_menu_item(child) for child in item.get_children().filter(is_active=True)]
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
    menu_items = MenuItem.objects.filter(parent=None, is_active=True).prefetch_related('children')

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
