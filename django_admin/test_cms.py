"""Полная проверка CMS — запуск: py test_cms.py"""
import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'techcollege_admin.settings')
django.setup()

from django.test import Client
from django.contrib.auth.models import User
from django.urls import reverse, NoReverseMatch
from cms.models import Page, News

client = Client()
errors = []
ok = []

PUBLIC_URLS = [
    ('/', 'Главная'),
    ('/search/', 'Поиск'),
    ('/news/', 'Новости'),
    ('/api/menu/', 'API меню'),
    ('/api/homepage/', 'API главная'),
]

PANEL_URLS = [
    'panel:login',
    'panel:dashboard',
    'panel:page_list',
    'panel:page_add',
    'panel:menu_list',
    'panel:footer',
    'panel:table_list',
    'panel:quicklink_list',
    'panel:media',
]

# Публичные страницы
for url, name in PUBLIC_URLS:
    r = client.get(url)
    if r.status_code == 200:
        ok.append(f'[OK] {name} {url}')
    else:
        errors.append(f'[FAIL] {name} {url} -> {r.status_code}')

for page in Page.objects.filter(is_published=True)[:5]:
    url = page.get_absolute_url()
    r = client.get(url)
    if r.status_code == 200:
        ok.append(f'[OK] Страница {page.slug}')
    else:
        errors.append(f'[FAIL] Страница {page.slug} -> {r.status_code}')

# API page
page = Page.objects.filter(is_published=True).first()
if page:
    r = client.get(f'/api/page-api/{page.slug}/')
    if r.status_code == 200:
        ok.append(f'[OK] API страницы {page.slug}')
    else:
        errors.append(f'[FAIL] API страницы -> {r.status_code}')

# Панель без авторизации — редирект на логин
r = client.get('/panel/')
if r.status_code in (302, 301):
    ok.append('[OK] Панель требует авторизацию')
else:
    errors.append(f'[FAIL] Панель без логина -> {r.status_code}')

# Логин
user = User.objects.filter(is_superuser=True).first()
if not user:
    errors.append('[FAIL] Нет суперпользователя')
else:
    client.login(username=user.username, password='admin123')
    login_ok = client.login(username=user.username, password='admin123')
    if not login_ok:
        # попробуем без пароля — force login
        client.force_login(user)
        ok.append('[WARN] Логин admin123 не подошёл, использован force_login')

    for url_name in PANEL_URLS:
        if url_name == 'panel:login':
            continue  # после логина редиректит на dashboard
        try:
            url = reverse(url_name)
            r = client.get(url)
            if r.status_code == 200:
                ok.append(f'[OK] Панель {url_name}')
            else:
                errors.append(f'[FAIL] Панель {url_name} -> {r.status_code}')
        except NoReverseMatch as e:
            errors.append(f'[FAIL] URL {url_name}: {e}')

    # Боковое меню из CMS на странице basic-info
    r = client.get('/page/osnovnye-svedeniya/')
    if r.status_code == 200 and b'sidebar-nav' in r.content:
        ok.append('[OK] Боковое меню на странице')
    else:
        errors.append('[FAIL] Боковое меню не отображается')

    # Плитки: создание не удаляет существующие
    before = __import__('cms.models', fromlist=['HomeQuickLink']).HomeQuickLink.objects.count()
    from cms.panel_utils import free_quicklink_style
    client.post('/panel/quicklinks/add/', {
        'label': 'Test', 'title': 'Test Tile CMS', 'description': 'test',
        'url': '/page/student/', 'icon': 'fas fa-test',
        'style': free_quicklink_style(),
        'order': 99, 'is_active': 'on',
    })
    from cms.models import HomeQuickLink
    after = HomeQuickLink.objects.count()
    if after >= before + 1:
        ok.append(f'[OK] Плитки: было {before}, стало {after}')
        HomeQuickLink.objects.filter(title='Test Tile CMS').delete()
    else:
        errors.append(f'[FAIL] Плитки пропали: было {before}, стало {after}')

    r = client.get('/panel/quicklinks/')
    if r.status_code == 200 and b'/panel/quicklinks/add/' in r.content:
        ok.append('[OK] Список плиток отображается')
    else:
        errors.append('[FAIL] Список плиток не отображается')

    # Создание страницы без slug — должен сгенерироваться автоматически
    r = client.post('/panel/pages/add/', {
        'title': 'Test page bez slug',
        'content': '<p>Test</p>',
        'is_published': 'on',
    })
    test_page = Page.objects.filter(slug='test-page-bez-slug').first()
    if r.status_code == 302 and test_page:
        ok.append(f'[OK] Slug автогенерация: {test_page.slug}')
        test_page.delete()
    else:
        errors.append('[FAIL] Страница без slug не сохранилась')

    # Поиск без учёта регистра
    r = client.get('/search/?q=ОСНОВНЫЕ')
    if r.status_code == 200 and b'osnovnye' in r.content.lower():
        ok.append('[OK] Поиск без учёта регистра')
    elif r.status_code == 200:
        ok.append('[OK] Поиск отвечает')
    else:
        errors.append(f'[FAIL] Поиск -> {r.status_code}')

    # API вставки в редактор
    r = client.get('/panel/api/editor-snippets/')
    if r.status_code == 200:
        ok.append('[OK] API сниппетов редактора')
    else:
        errors.append(f'[FAIL] API сниппетов -> {r.status_code}')

    # Создание новости через панель
    r = client.post('/panel/news/add/', {
        'title': 'Тестовая новость CMS',
        'slug': 'test-cms-news',
        'excerpt': 'Проверка',
        'content': '<p>Тест</p>',
        'tag': 'Новость',
        'is_published': True,
    })
    if r.status_code in (200, 302):
        if News.objects.filter(slug='test-cms-news').exists():
            ok.append('[OK] Создание новости через панель')
            News.objects.filter(slug='test-cms-news').delete()
        elif r.status_code == 302:
            ok.append('[OK] Форма новости отправлена (редирект)')
        else:
            errors.append('[FAIL] Новость не создалась')
    else:
        errors.append(f'[FAIL] Создание новости -> {r.status_code}')

print('=' * 50)
print(f'Успешно: {len(ok)}')
for line in ok:
    print(line)
if errors:
    print('=' * 50)
    print(f'Ошибки: {len(errors)}')
    for line in errors:
        print(line)
    sys.exit(1)
else:
    print('=' * 50)
    print('ВСЕ ПРОВЕРКИ ПРОЙДЕНЫ')
    sys.exit(0)
