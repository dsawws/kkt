"""
Абсолютная проверка всего CMS.
Запуск из django_admin/:  py full_audit.py
"""
import os
import sys
import io
import re
from pathlib import Path

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'techcollege_admin.settings')

import django
django.setup()

from django.conf import settings
from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client
from django.urls import reverse, get_resolver, NoReverseMatch
from django.template.loader import get_template

from cms.models import (
    Page, News, Document, DocumentSection, MenuItem, HomePage, HomeQuickLink,
    HomeBlock, Banner, Gallery, ContentBlock, ContentTable, EducationalProgram,
    AdmissionYear, ProgramDocument,
)
from cms.embed_utils import (
    table_embed_tag, expand_content_embeds, normalize_content_embeds, content_for_editor,
)
from cms.snippet_utils import document_snippet_html
from cms.search_utils import search_pages
from cms.panel_utils import free_quicklink_style, next_quicklink_order, sync_page_to_menu

ok, fail, warn = [], [], []


def PASS(msg):
    ok.append(msg)
    try:
        print(f'  [OK] {msg}')
    except UnicodeEncodeError:
        print(f'  [OK] {msg}'.encode('ascii', 'replace').decode('ascii'))


def FAIL(msg):
    fail.append(msg)
    try:
        print(f'[FAIL] {msg}')
    except UnicodeEncodeError:
        print(f'[FAIL] {msg}'.encode('ascii', 'replace').decode('ascii'))


def WARN(msg):
    warn.append(msg)
    try:
        print(f'[WARN] {msg}')
    except UnicodeEncodeError:
        print(f'[WARN] {msg}'.encode('ascii', 'replace').decode('ascii'))


client = Client()
print('=' * 60)
print('1. SETTINGS & PATHS')
print('=' * 60)

PASS(f'DEBUG={settings.DEBUG}')
PASS(f'STATIC_ROOT={settings.STATIC_ROOT}')
PASS(f'MEDIA_ROOT={settings.MEDIA_ROOT}')
if (Path(settings.BASE_DIR) / 'static').is_dir():
    PASS('django_admin/static существует')
else:
    FAIL('django_admin/static отсутствует')

frontend_in_static = any(
    'frontend' in str(p).replace('\\', '/')
    for p in getattr(settings, 'STATICFILES_DIRS', [])
)
if frontend_in_static:
    FAIL('frontend/ всё ещё в STATICFILES_DIRS — нельзя для collectstatic')
else:
    PASS('STATICFILES_DIRS без frontend/ (только django_admin/static)')

print()
print('=' * 60)
print('2. STATICFILES (collectstatic)')
print('=' * 60)

root = Path(settings.STATIC_ROOT)
must = [
    'style.css', 'script.js', 'media-styles.css', 'vk-widget.js',
    'css/responsive.css', 'img/logo.png', 'img/VOV.jpg',
    'panel/admin.css', 'panel/slugify.js', 'panel/editor-tools.js',
    'ckeditor/ckeditor/ckeditor.js', 'admin/css/base.css',
]
if not root.is_dir():
    FAIL(f'STATIC_ROOT нет: {root}')
else:
    n = sum(1 for _ in root.rglob('*') if _.is_file())
    PASS(f'Файлов в staticfiles: {n}')
    for rel in must:
        if (root / rel).is_file():
            PASS(f'  {rel}')
        else:
            FAIL(f'  нет {rel}')
    for d in ('ckeditor', 'admin', 'mptt', 'panel', 'css', 'img'):
        if (root / d).is_dir():
            PASS(f'  dir {d}/')
        else:
            WARN(f'  нет dir {d}/')

print()
print('=' * 60)
print('3. TEMPLATES LOAD')
print('=' * 60)

templates = [
    'cms/base.html', 'cms/index.html', 'cms/page_detail.html', 'cms/page_professions.html',
    'cms/news_list.html', 'cms/news_detail.html', 'cms/search.html',
    'panel/base.html', 'panel/page_form.html', 'panel/menu_form.html',
    'panel/program_form.html', 'panel/table_form.html', 'panel/quicklink_form.html',
    'panel/user_list.html', 'panel/admission_year_list.html', 'panel/login.html',
]
for t in templates:
    try:
        get_template(t)
        PASS(t)
    except Exception as e:
        FAIL(f'{t}: {e}')

print()
print('=' * 60)
print('4. URL REVERSE (panel + cms)')
print('=' * 60)

panel_names = [
    'panel:login', 'panel:dashboard', 'panel:page_list', 'panel:page_add',
    'panel:news_list', 'panel:news_add', 'panel:document_list', 'panel:document_add',
    'panel:menu_list', 'panel:menu_add', 'panel:footer', 'panel:table_list', 'panel:table_add',
    'panel:quicklink_list', 'panel:quicklink_add', 'panel:banner_list', 'panel:banner_add',
    'panel:program_list', 'panel:program_add', 'panel:admission_year_list',
    'panel:media', 'panel:user_list', 'panel:user_add', 'panel:homepage',
    'panel:api_editor_snippets',
]
for name in panel_names:
    try:
        reverse(name)
        PASS(name)
    except NoReverseMatch as e:
        FAIL(f'{name}: {e}')

cms_names = ['cms:index', 'cms:search', 'cms:news_list', 'cms:api_menu', 'cms:api_homepage']
for name in cms_names:
    try:
        reverse(name)
        PASS(name)
    except NoReverseMatch as e:
        FAIL(f'{name}: {e}')

print()
print('=' * 60)
print('5. PUBLIC SITE HTTP')
print('=' * 60)

public = [
    ('/', 'Главная'),
    ('/search/', 'Поиск пустой'),
    ('/search/?q=ТЕСТ', 'Поиск'),
    ('/news/', 'Новости'),
    ('/page/professions/', 'Специальности'),
    ('/page/obrazovanie/', 'Образование'),
    ('/page/osnovnye-svedeniya/', 'Основные сведения'),
    ('/page/abiturient/', 'Поступающим'),
    ('/page/student/', 'Студентам'),
    ('/api/menu/', 'API menu'),
    ('/api/homepage/', 'API homepage'),
]
for url, title in public:
    r = client.get(url)
    if r.status_code == 200:
        PASS(f'{title} {url}')
    else:
        FAIL(f'{title} {url} -> {r.status_code}')

# all published pages
broken_pages = []
for p in Page.objects.filter(is_published=True):
    r = client.get(p.get_absolute_url())
    if r.status_code != 200:
        broken_pages.append(f'{p.slug}:{r.status_code}')
if broken_pages:
    FAIL(f'Страницы с ошибкой: {broken_pages[:10]}')
else:
    PASS(f'Все опубликованные страницы OK ({Page.objects.filter(is_published=True).count()})')

r = client.get('/')
html = r.content.decode('utf-8', 'replace')
for needle in ['/static/style.css', '/static/script.js', '/static/img/logo.png', 'nav-list']:
    if needle in html:
        PASS(f'Главная содержит {needle}')
    else:
        FAIL(f'Главная без {needle}')

r = client.get('/page/professions/')
if b'profession-card' in r.content:
    PASS('Специальности: карточки')
elif b'professions-empty' in r.content:
    WARN('Специальности: пусто (нет программ)')
else:
    FAIL('Специальности: неожиданный шаблон')

print()
print('=' * 60)
print('6. AUTH & PANEL ACCESS')
print('=' * 60)

r = client.get('/panel/')
if r.status_code in (301, 302):
    PASS('Panel without login redirects')
else:
    FAIL(f'Panel without login -> {r.status_code}')

user = User.objects.filter(is_superuser=True).first()
if not user:
    FAIL('Нет суперпользователя')
    print('Создайте: py manage.py createsuperuser')
    sys.exit(1)
PASS(f'Суперпользователь: {user.username}')
client.force_login(user)

for name in panel_names:
    if name == 'panel:login':
        continue
    try:
        url = reverse(name)
    except NoReverseMatch:
        continue
    r = client.get(url)
    if r.status_code == 200:
        PASS(f'GET {name}')
    else:
        FAIL(f'GET {name} -> {r.status_code}')

r = client.get(reverse('panel:page_add'))
body = r.content.lower()
if b'ckeditor' in body:
    PASS('CKEditor подключён на форме страницы')
else:
    FAIL('CKEditor не найден на форме страницы')

print()
print('=' * 60)
print('7. CRUD FULL CYCLE')
print('=' * 60)

# Page
r = client.post('/panel/pages/add/', {
    'title': 'Audit Page Full',
    'content': '<p>audit-v1</p>',
    'is_published': 'on',
})
page = Page.objects.filter(slug='audit-page-full').first()
if page and r.status_code == 302:
    PASS('Page create')
else:
    FAIL(f'Page create status={r.status_code}')

if page:
    r = client.post(f'/panel/pages/{page.pk}/edit/', {
        'title': 'Audit Page Full',
        'slug': page.slug,
        'content': '<p>audit-v2</p>',
        'is_published': 'on',
        'order': '0',
    })
    page.refresh_from_db()
    if 'audit-v2' in (page.content or ''):
        PASS('Page edit')
    else:
        FAIL(f'Page edit content={page.content!r} status={r.status_code}')
    r = client.get(page.get_absolute_url())
    if r.status_code == 200 and b'audit-v2' in r.content:
        PASS('Page visible on site')
    else:
        FAIL('Page not visible on site')

# Table embed
r = client.post('/panel/tables/add/', {
    'title': 'Audit Table',
    'content': '<table><tr><td>A1</td></tr></table>',
})
table = ContentTable.objects.filter(slug='audit-table').first()
if table:
    PASS('Table create')
    tag = table_embed_tag(table.slug)
    if page:
        page.content = f'<div>{tag}</div>'
        page.save()
        exp = expand_content_embeds(page.content)
        if 'A1' in exp and '[[cms-table' not in exp:
            PASS('Table embed expand')
        else:
            FAIL(f'Table embed expand: {exp[:120]}')
        table.content = '<table><tr><td>B2</td></tr></table>'
        table.save()
        exp2 = expand_content_embeds(page.content)
        if 'B2' in exp2:
            PASS('Table sync after edit')
        else:
            FAIL('Table sync failed')
    # API returns placeholder not raw HTML copy
    r = client.get(f'/panel/api/tables/{table.pk}/')
    data = r.json() if r.status_code == 200 else {}
    if 'cms-embed-table' in data.get('html', '') or data.get('tag', '').startswith('[[cms-table'):
        PASS('API table = reference placeholder')
    else:
        FAIL(f'API table returns copy? keys={list(data.keys())}')
else:
    FAIL('Table create')

# Document
try:
    from PIL import Image
    bio = io.BytesIO()
    Image.new('RGB', (8, 8), (0, 128, 0)).save(bio, format='PNG')
    png = bio.getvalue()
except Exception:
    png = (
        b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01'
        b'\x08\x02\x00\x00\x00\x90wS\xde\x00\x00\x00\x0cIDATx\x9cc\xf8\x0f\x00'
        b'\x00\x01\x01\x00\x05\x18\xd8N\x00\x00\x00\x00IEND\xaeB`\x82'
    )

pdf = SimpleUploadedFile('audit.pdf', b'%PDF-1.4 audit', content_type='application/pdf')
r = client.post('/panel/documents/add/', {
    'title': 'Audit Doc',
    'category': 'other',
    'page': page.pk if page else '',
    'file': pdf,
    'is_active': 'on',
    'order': '0',
})
doc = Document.objects.filter(title='Audit Doc').first()
if doc and doc.file:
    PASS('Document create+file')
    snip = document_snippet_html(doc)
    if 'document-item' in snip and 'download-btn' in snip:
        PASS('Document snippet = download block')
    else:
        FAIL('Document snippet wrong')
    r = client.get(f'/panel/api/documents/{doc.pk}/')
    if r.status_code == 200 and 'document-item' in r.json().get('html', ''):
        PASS('API document snippet')
    else:
        FAIL('API document snippet')
else:
    FAIL(f'Document create status={r.status_code}')

# News
r = client.post('/panel/news/add/', {
    'title': 'Audit News',
    'slug': 'audit-news',
    'excerpt': 'ex',
    'content': '<p>n</p>',
    'tag': 'Новость',
    'is_published': 'on',
})
news = News.objects.filter(slug='audit-news').first()
if news:
    PASS('News create')
    r = client.get(news.get_absolute_url())
    if r.status_code == 200:
        PASS('News on site')
    else:
        FAIL(f'News on site -> {r.status_code}')
else:
    FAIL(f'News create status={r.status_code}')

# Program
prof = Page.objects.filter(slug='professions').first()
r = client.post('/panel/programs/add/', {
    'title': 'Audit Spec',
    'code': '00.00.00',
    'qualification': 'аудитор',
    'duration': '1 год',
    'form': 'Очная',
    'icon': 'fas fa-check',
    'description': 'desc',
    'page': prof.pk if prof else '',
    'show_on_homepage': 'on',
    'is_active': 'on',
    'order': '100',
})
prog = EducationalProgram.objects.filter(code='00.00.00').first()
if prog:
    PASS('Program create')
    r = client.get('/page/professions/')
    if b'Audit Spec' in r.content:
        PASS('Program on professions page')
    else:
        FAIL('Program not on professions page')
    r = client.get('/')
    if b'Audit Spec' in r.content or '00.00.00'.encode() in r.content:
        PASS('Program on homepage list')
    else:
        WARN('Program not in homepage teaser (может быть лимит отображения)')
else:
    FAIL(f'Program create status={r.status_code}')

# Banner
img = SimpleUploadedFile('audit-banner.png', png, content_type='image/png')
r = client.post('/panel/banners/add/', {
    'title': 'Audit Banner',
    'image': img,
    'url': 'https://example.com',
    'order': '0',
    'is_active': 'on',
})
banner = Banner.objects.filter(title='Audit Banner').first()
if banner:
    PASS('Banner create')
else:
    FAIL(f'Banner create status={r.status_code}')

# Quicklink
HomeQuickLink.objects.filter(title='Audit Tile').delete()
r = client.post('/panel/quicklinks/add/', {
    'label': 'A',
    'title': 'Audit Tile',
    'description': 'd',
    'url': '/',
    'icon': 'fas fa-star',
    'style': free_quicklink_style() or 'bento-g2',
    'order': str(next_quicklink_order()),
    'is_active': 'on',
})
tile = HomeQuickLink.objects.filter(title='Audit Tile').first()
if tile:
    PASS('Quicklink create')
else:
    FAIL(f'Quicklink create status={r.status_code}')

# Footer
r = client.post('/panel/footer/', {
    'footer_tagline': 'Audit tagline XYZ',
    'footer_copyright': 'Copyright Audit 2026',
    'contacts_address': 'addr',
    'contacts_phone': '111',
    'contacts_email': 'audit@kktbel.ru',
    'site_vk': 'https://vk.com/belkkt',
    'site_telegram': 'https://t.me/belkkt',
})
if r.status_code == 302:
    PASS('Footer save')
    r = client.get('/')
    if b'Audit tagline XYZ' in r.content:
        PASS('Footer on site')
    else:
        hp = HomePage.load()
        FAIL(f'Footer text not on site (db={hp.footer_tagline!r})')
else:
    FAIL(f'Footer save status={r.status_code} (ожидался редирект 302)')

# Menu
r = client.get('/panel/menu/')
if r.status_code == 200:
    PASS('Menu list')
else:
    FAIL('Menu list')

# Users
r = client.get('/panel/users/')
if r.status_code == 200:
    PASS('Users list')
else:
    FAIL(f'Users list {r.status_code}')

# Media
r = client.get('/panel/media/')
if r.status_code == 200:
    PASS('Media library')
else:
    FAIL('Media library')

# Slug validation
r = client.post('/panel/pages/add/', {
    'title': 'Slug Auto Audit',
    'content': '<p>x</p>',
    'is_published': 'on',
})
sp = Page.objects.filter(title='Slug Auto Audit').first()
if sp and sp.slug:
    PASS(f'Slug autogen: {sp.slug}')
    sp.delete()
else:
    FAIL('Slug autogen')

# Search case-insensitive
Page.objects.filter(slug='audit-search-case').delete()
Page.objects.create(title='УникальныйАудитРегистр', slug='audit-search-case', content='x', is_published=True)
found = search_pages(Page.objects.all(), 'уникальныйаудитрегистр')
if found.filter(slug='audit-search-case').exists():
    PASS('Search case-insensitive (Cyrillic)')
else:
    FAIL('Search case-insensitive')
Page.objects.filter(slug='audit-search-case').delete()

print()
print('=' * 60)
print('8. DATA INTEGRITY')
print('=' * 60)

PASS(f'Pages: {Page.objects.count()}')
PASS(f'Programs: {EducationalProgram.objects.filter(is_active=True).count()}')
PASS(f'Menu top: {MenuItem.objects.filter(parent=None, is_active=True).count()}')
PASS(f'Documents: {Document.objects.count()}')
PASS(f'Tables: {ContentTable.objects.count()}')
PASS(f'Banners: {Banner.objects.count()}')
PASS(f'Tiles: {HomeQuickLink.objects.count()}')

empty_slug = Page.objects.filter(slug='').count() + Page.objects.filter(slug__isnull=True).count()
if empty_slug:
    FAIL(f'Страницы с пустым slug: {empty_slug}')
else:
    PASS('Нет страниц с пустым slug')

print()
print('=' * 60)
print('9. DEPLOY ARTIFACTS')
print('=' * 60)

repo = Path(settings.BASE_DIR).parent
deploy_files = [
    'deploy/nginx-new.kktbel.ru.conf',
    'deploy/kktbel.service',
    'deploy/collectstatic.sh',
    'deploy/README.md',
]
for rel in deploy_files:
    if (repo / rel).is_file():
        PASS(rel)
    else:
        FAIL(f'нет {rel}')

nginx = (repo / 'deploy/nginx-new.kktbel.ru.conf').read_text(encoding='utf-8')
checks_ngx = [
    ('127.0.0.1:8041', 'proxy на 8041'),
    ('new.kktbel.ru', 'server_name'),
    ('staticfiles/', 'static → staticfiles'),
    ('django_admin/media/', 'media'),
    ('location /static/', 'location static'),
]
for needle, label in checks_ngx:
    if needle in nginx:
        PASS(f'nginx: {label}')
    else:
        FAIL(f'nginx: нет {label}')
if 'try_files' in nginx and 'location /static/' in nginx:
    # try_files with alias is bad — we removed it
    static_block = re.search(r'location /static/\{.*?\}', nginx, re.S)
    if static_block and 'try_files' in static_block.group(0):
        FAIL('nginx: try_files в /static/ (ломает alias)')
    else:
        PASS('nginx: /static/ без try_files')

print()
print('=' * 60)
print('10. CLEANUP')
print('=' * 60)

Document.objects.filter(title='Audit Doc').delete()
ContentTable.objects.filter(slug='audit-table').delete()
EducationalProgram.objects.filter(code='00.00.00').delete()
Banner.objects.filter(title='Audit Banner').delete()
HomeQuickLink.objects.filter(title='Audit Tile').delete()
News.objects.filter(slug='audit-news').delete()
Page.objects.filter(slug='audit-page-full').delete()
Page.objects.filter(slug='audit-search-case').delete()

# restore footer defaults if audit changed them
hp = HomePage.load()
if hp.footer_tagline == 'Audit tagline XYZ':
    hp.footer_tagline = 'Качество образование — наша главная цель'
    hp.footer_copyright = '© 2026 Техникум. Все права защищены.'
    hp.save(update_fields=['footer_tagline', 'footer_copyright'])
PASS('Тестовые объекты удалены')

print()
print('=' * 60)
print(f'ИТОГО: OK={len(ok)}  WARN={len(warn)}  FAIL={len(fail)}')
print('=' * 60)
if fail:
    print('ПРОВАЛЫ:')
    for f in fail:
        print(f'  - {f}')
    sys.exit(1)
if warn:
    print('Предупреждения:')
    for w in warn:
        print(f'  - {w}')
print('АБСОЛЮТНАЯ ПРОВЕРКА ПРОЙДЕНА')
sys.exit(0)
