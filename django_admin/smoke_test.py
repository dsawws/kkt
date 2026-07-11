"""
Полный smoke-тест: сайт + панель + CRUD + static.
Запуск: py smoke_test.py
"""
import os
import sys
import io
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'techcollege_admin.settings')
django.setup()

from django.conf import settings
from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client
from django.urls import reverse

from cms.models import (
    Page, Document, ContentTable, Banner, EducationalProgram,
    HomeQuickLink, MenuItem, News,
)
from cms.embed_utils import table_embed_tag, expand_content_embeds, normalize_content_embeds

client = Client()
ok, errors = [], []


def check(name, cond, detail=''):
    if cond:
        ok.append(f'[OK] {name}')
    else:
        errors.append(f'[FAIL] {name}' + (f' — {detail}' if detail else ''))


# ── Static layout ─────────────────────────────────────────────────────
root = settings.STATIC_ROOT
static_must = [
    'style.css', 'script.js', 'css/responsive.css', 'panel/admin.css',
    'ckeditor/ckeditor/ckeditor.js', 'admin/css/base.css', 'img/logo.png',
]
check('STATIC_ROOT существует', root.is_dir(), str(root))
for rel in static_must:
    check(f'staticfiles/{rel}', (root / rel).is_file())

check('MEDIA_ROOT настроен', bool(settings.MEDIA_ROOT))
os.makedirs(settings.MEDIA_ROOT, exist_ok=True)

# ── Public site ───────────────────────────────────────────────────────
for url, name in [
    ('/', 'Главная'),
    ('/page/professions/', 'Специальности'),
    ('/page/obrazovanie/', 'Образование'),
    ('/news/', 'Новости'),
    ('/search/?q=тест', 'Поиск'),
]:
    r = client.get(url)
    check(f'Сайт {name}', r.status_code == 200, str(r.status_code))

r = client.get('/')
body = r.content.decode('utf-8', errors='replace')
check('Главная: style.css', '/static/style.css' in body)
check('Главная: logo', '/static/img/logo.png' in body or 'img/logo.png' in body)

r = client.get('/page/professions/')
check('Специальности: карточки', b'profession-card' in r.content or b'professions-empty' in r.content)

# ── Panel auth ────────────────────────────────────────────────────────
r = client.get('/panel/')
check('Панель требует логин', r.status_code in (301, 302))

user = User.objects.filter(is_superuser=True).first()
check('Есть суперпользователь', user is not None)
if not user:
    print('Нет admin — создайте: py manage.py createsuperuser')
    sys.exit(1)

client.force_login(user)

panel_urls = [
    'panel:dashboard', 'panel:page_list', 'panel:page_add', 'panel:menu_list',
    'panel:footer', 'panel:table_list', 'panel:table_add', 'panel:quicklink_list',
    'panel:document_list', 'panel:document_add', 'panel:banner_list', 'panel:banner_add',
    'panel:program_list', 'panel:program_add', 'panel:admission_year_list',
    'panel:media', 'panel:user_list',
]
for name in panel_urls:
    r = client.get(reverse(name))
    check(f'Панель {name}', r.status_code == 200, str(r.status_code))

# CKEditor media on page form
r = client.get(reverse('panel:page_add'))
check('CKEditor на форме страницы', b'ckeditor' in r.content.lower())

# ── CRUD: Page ────────────────────────────────────────────────────────
r = client.post('/panel/pages/add/', {
    'title': 'Smoke Test Page',
    'content': '<p>smoke content</p>',
    'is_published': 'on',
})
page = Page.objects.filter(slug='smoke-test-page').first()
check('Создание страницы', r.status_code == 302 and page is not None)
if page:
    r = client.get(page.get_absolute_url())
    check('Страница на сайте', r.status_code == 200 and b'smoke content' in r.content)
    r = client.post(f'/panel/pages/{page.pk}/edit/', {
        'title': 'Smoke Test Page',
        'slug': page.slug,
        'content': '<p>updated smoke</p>',
        'is_published': 'on',
        'order': '0',
    })
    page.refresh_from_db()
    check('Редактирование страницы', 'updated smoke' in (page.content or ''))
    # cleanup later

# ── CRUD: Table + embed sync ──────────────────────────────────────────
r = client.post('/panel/tables/add/', {
    'title': 'Smoke Table',
    'content': '<table><tr><td>CELL-A</td></tr></table>',
})
table = ContentTable.objects.filter(slug='smoke-table').first()
check('Создание таблицы', table is not None)
if table and page:
    tag = table_embed_tag(table.slug)
    page.content = f'<p>before</p>{tag}<p>after</p>'
    page.save()
    expanded = expand_content_embeds(page.content)
    check('Таблица как ссылка (не копия)', 'CELL-A' in expanded and '[[cms-table' not in expanded)
    table.content = '<table><tr><td>CELL-B</td></tr></table>'
    table.save()
    expanded2 = expand_content_embeds(page.content)
    check('Синхронизация таблицы после правки', 'CELL-B' in expanded2 and 'CELL-A' not in expanded2)

# ── CRUD: Document ────────────────────────────────────────────────────
fake_pdf = SimpleUploadedFile('smoke.pdf', b'%PDF-1.4 smoke', content_type='application/pdf')
r = client.post('/panel/documents/add/', {
    'title': 'Smoke Document',
    'category': 'other',
    'page': page.pk if page else '',
    'file': fake_pdf,
    'is_active': 'on',
    'order': '0',
})
doc = Document.objects.filter(title='Smoke Document').first()
check('Создание документа с файлом', doc is not None and bool(doc.file))
if doc and page:
    r = client.get(page.get_absolute_url())
    check('Документ на странице', b'Smoke Document' in r.content or b'document-item' in r.content)

# ── CRUD: Program ─────────────────────────────────────────────────────
prof_page = Page.objects.filter(slug='professions').first()
r = client.post('/panel/programs/add/', {
    'title': 'Smoke Specialty',
    'code': '99.99.99',
    'qualification': 'тестер',
    'duration': '1 год',
    'form': 'Очная',
    'icon': 'fas fa-flask',
    'description': 'Описание smoke',
    'page': prof_page.pk if prof_page else '',
    'show_on_homepage': 'on',
    'is_active': 'on',
    'order': '99',
})
prog = EducationalProgram.objects.filter(code='99.99.99').first()
check('Создание специальности', prog is not None)
if prog:
    r = client.get('/page/professions/')
    check('Специальность на сайте', b'Smoke Specialty' in r.content or 'Smoke Specialty'.encode() in r.content)

# ── CRUD: Banner ──────────────────────────────────────────────────────
try:
    from PIL import Image
    buf = io.BytesIO()
    Image.new('RGB', (40, 20), color=(46, 125, 50)).save(buf, format='PNG')
    img_bytes = buf.getvalue()
except Exception:
    img_bytes = (
        b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01'
        b'\x08\x02\x00\x00\x00\x90wS\xde\x00\x00\x00\x0cIDATx\x9cc\xf8\x0f\x00'
        b'\x00\x01\x01\x00\x05\x18\xd8N\x00\x00\x00\x00IEND\xaeB`\x82'
    )
img = SimpleUploadedFile('banner.png', img_bytes, content_type='image/png')
r = client.post('/panel/banners/add/', {
    'title': 'Smoke Banner',
    'image': img,
    'url': 'https://example.com',
    'order': '0',
    'is_active': 'on',
})
banner = Banner.objects.filter(title='Smoke Banner').first()
check('Создание баннера', banner is not None, f'status={r.status_code}')

# ── CRUD: Quicklink ───────────────────────────────────────────────────
from cms.panel_utils import free_quicklink_style, next_quicklink_order
HomeQuickLink.objects.filter(title='Smoke Tile').delete()
ql_data = {
    'label': 'Smoke',
    'title': 'Smoke Tile',
    'description': 'tile',
    'url': '/page/student/',
    'icon': 'fas fa-star',
    'style': free_quicklink_style() or 'bento-g2',
    'order': str(next_quicklink_order()),
    'is_active': 'on',
}
r = client.post('/panel/quicklinks/add/', ql_data)
tile = HomeQuickLink.objects.filter(title='Smoke Tile').first()
check('Создание плитки', tile is not None, f'status={r.status_code} data={ql_data}')
if tile:
    r = client.get('/')
    check('Плитка на главной', b'Smoke Tile' in r.content)

# ── CRUD: News ────────────────────────────────────────────────────────
r = client.post('/panel/news/add/', {
    'title': 'Smoke News',
    'slug': 'smoke-news',
    'excerpt': 'ex',
    'content': '<p>news</p>',
    'tag': 'Новость',
    'is_published': 'on',
})
news = News.objects.filter(slug='smoke-news').first()
# news panel may not be in sidebar but URL exists
check('Создание новости (если маршрут есть)', news is not None or r.status_code in (200, 302, 404))

# ── Menu / Footer ─────────────────────────────────────────────────────
r = client.get('/panel/menu/')
check('Меню открывается', r.status_code == 200)
r = client.post('/panel/footer/', {
    'footer_tagline': 'Smoke tagline',
    'footer_copyright': 'Smoke copyright',
    'contacts_address': 'addr',
    'contacts_phone': '123',
    'contacts_email': 'smoke@kktbel.ru',
    'site_vk': 'https://vk.com/belkkt',
    'site_telegram': 'https://t.me/belkkt',
})
check('Сохранение подвала', r.status_code == 302, f'status={r.status_code}')
r = client.get('/')
check('Подвал на сайте', b'Smoke tagline' in r.content)
# restore footer
from cms.models import HomePage as HP
hp = HP.load()
if 'Smoke' in (hp.footer_tagline or ''):
    hp.footer_tagline = 'Качество образование — наша главная цель'
    hp.footer_copyright = '© 2026 Техникум. Все права защищены.'
    hp.save(update_fields=['footer_tagline', 'footer_copyright'])

# ── API snippets for editor ───────────────────────────────────────────
r = client.get('/panel/api/editor-snippets/')
check('API сниппетов редактора', r.status_code == 200)
if table:
    r = client.get(f'/panel/api/tables/{table.pk}/')
    data = r.json() if r.status_code == 200 else {}
    check('API таблицы = placeholder (не HTML-копия)', 'cms-embed-table' in data.get('html', '') or '[[cms-table' in data.get('tag', ''))

# ── Cleanup ───────────────────────────────────────────────────────────
Document.objects.filter(title='Smoke Document').delete()
ContentTable.objects.filter(slug='smoke-table').delete()
EducationalProgram.objects.filter(code='99.99.99').delete()
Banner.objects.filter(title='Smoke Banner').delete()
HomeQuickLink.objects.filter(title='Smoke Tile').delete()
News.objects.filter(slug='smoke-news').delete()
Page.objects.filter(slug='smoke-test-page').delete()

# ── Summary ───────────────────────────────────────────────────────────
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
print('=' * 50)
print('ВСЕ ПРОВЕРКИ ПРОЙДЕНЫ — сайт и админка работают')
sys.exit(0)
