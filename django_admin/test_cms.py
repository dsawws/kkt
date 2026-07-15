"""Полная проверка CMS — запуск: py test_cms.py"""
import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'techcollege_admin.settings')
django.setup()

from django.test import Client
from django.contrib.auth.models import User
from django.urls import reverse, NoReverseMatch
from cms.models import Page, News, EducationalProgram, ContentTable
from cms.embed_utils import table_embed_tag, expand_content_embeds

client = Client()
errors = []
ok = []

PUBLIC_URLS = [
    ('/', 'Главная'),
    ('/search/', 'Поиск'),
    ('/news/', 'Новости'),
    ('/page/professions/', 'Специальности'),
    ('/page/obrazovanie/', 'Образование'),
    ('/api/menu/', 'API меню'),
    ('/api/homepage/', 'API главная'),
]

PANEL_URLS = [
    'panel:dashboard',
    'panel:page_list',
    'panel:page_add',
    'panel:menu_list',
    'panel:footer',
    'panel:table_list',
    'panel:quicklink_list',
    'panel:media',
    'panel:document_list',
    'panel:banner_list',
    'panel:program_list',
    'panel:program_add',
    'panel:admission_year_list',
]

for url, name in PUBLIC_URLS:
    r = client.get(url)
    if r.status_code == 200:
        ok.append(f'[OK] {name} {url}')
    else:
        errors.append(f'[FAIL] {name} {url} -> {r.status_code}')

r = client.get('/page/professions/')
if r.status_code == 200:
    if b'profession-card' in r.content or b'professions-empty' in r.content:
        ok.append('[OK] Шаблон страницы специальностей')
    else:
        errors.append('[FAIL] Страница специальностей без карточек')

for page in Page.objects.filter(is_published=True)[:8]:
    url = page.get_absolute_url()
    r = client.get(url)
    if r.status_code == 200:
        ok.append(f'[OK] Страница {page.slug}')
    else:
        errors.append(f'[FAIL] Страница {page.slug} -> {r.status_code}')

page = Page.objects.filter(is_published=True).first()
if page:
    r = client.get(f'/api/page-api/{page.slug}/')
    if r.status_code == 200:
        ok.append(f'[OK] API страницы {page.slug}')
    else:
        errors.append(f'[FAIL] API страницы -> {r.status_code}')

r = client.get('/panel/')
if r.status_code in (302, 301):
    ok.append('[OK] Панель требует авторизацию')
else:
    errors.append(f'[FAIL] Панель без логина -> {r.status_code}')

user = User.objects.filter(is_superuser=True).first()
if not user:
    errors.append('[FAIL] Нет суперпользователя')
else:
    client.force_login(user)

    for url_name in PANEL_URLS:
        try:
            url = reverse(url_name)
            r = client.get(url)
            if r.status_code == 200:
                ok.append(f'[OK] Панель {url_name}')
            else:
                errors.append(f'[FAIL] Панель {url_name} -> {r.status_code}')
        except NoReverseMatch as e:
            errors.append(f'[FAIL] URL {url_name}: {e}')

    r = client.get('/panel/users/')
    if r.status_code == 200:
        ok.append('[OK] Панель panel:users (суперпользователь)')
    elif r.status_code == 302:
        ok.append('[OK] Пользователи — редирект')

    r = client.get('/page/osnovnye-svedeniya/')
    if r.status_code == 200 and b'sidebar-nav' in r.content:
        ok.append('[OK] Боковое меню на странице')
    else:
        errors.append('[FAIL] Боковое меню не отображается')

  # Таблицы: переиспользуемый embed
    table, _ = ContentTable.objects.get_or_create(
        slug='test-embed-table',
        defaults={'title': 'Test Table', 'content': '<table><tr><td>X</td></tr></table>'},
    )
    tag = table_embed_tag('test-embed-table')
    expanded = expand_content_embeds(f'<p>{tag}</p>')
    if 'X' in expanded and '[[cms-table' not in expanded:
        ok.append('[OK] Синхронизация таблиц (embed)')
    else:
        errors.append('[FAIL] Embed таблицы не раскрывается')

    r = client.post('/panel/pages/add/', {
        'title': 'Test page bez slug',
        'content': '<p>Test</p>',
        'is_published': 'on',
    })
    test_page = Page.objects.filter(slug='test-page-bez-slug').first()
    if r.status_code == 302 and test_page:
        ok.append('[OK] Slug автогенерация')
        test_page.delete()
    else:
        errors.append('[FAIL] Страница без slug не сохранилась')

    r = client.get('/search/?q=test')
    if r.status_code == 200:
        ok.append('[OK] Поиск')
    else:
        errors.append(f'[FAIL] Поиск -> {r.status_code}')

    r = client.get('/panel/api/editor-snippets/')
    if r.status_code == 200:
        ok.append('[OK] API сниппетов редактора')
    else:
        errors.append(f'[FAIL] API сниппетов -> {r.status_code}')

    prog_count = EducationalProgram.objects.filter(is_active=True).count()
    if prog_count > 0:
        ok.append(f'[OK] Программ в базе: {prog_count}')
    else:
        errors.append('[FAIL] Нет образовательных программ — запустите: py manage.py create_initial_data')

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
