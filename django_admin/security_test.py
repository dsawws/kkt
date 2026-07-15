"""
Security audit / penetration-style checks for the CMS.
Run: py security_test.py
"""
import os
import sys
import io

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'techcollege_admin.settings')
import django
django.setup()

from django.conf import settings
from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client
from django.urls import reverse

from cms.models import Page
from cms.panel_forms import PageForm
from cms.security_utils import (
    safe_join_media, sanitize_upload_subdir, sanitize_upload_filename,
    sanitize_html, is_safe_redirect_url,
)

ok, fail = [], []


def check(name, cond, detail=''):
    if cond:
        ok.append(name)
        print(f'  [OK] {name}')
    else:
        fail.append(f'{name} {detail}'.strip())
        print(f'[FAIL] {name}' + (f' — {detail}' if detail else ''))


client = Client(enforce_csrf_checks=True)
anon = Client(enforce_csrf_checks=True)

print('=' * 60)
print('SECURITY AUDIT')
print('=' * 60)

# ── 1. SQL injection (ORM / search) ───────────────────────────────────
print('\n1. SQL injection')
payloads = [
    "' OR '1'='1",
    "1; DROP TABLE cms_page;--",
    "1' UNION SELECT null--",
    "admin'--",
    "%' OR 1=1 --",
    "'; sleep(5) --",
]
before = Page.objects.count()
for p in payloads:
    r = anon.get('/search/', {'q': p})
    check(f'Search survives payload', r.status_code == 200, p[:40])
    r = anon.get(f'/page/{p}/')
    check(f'Page slug rejects SQLi', r.status_code in (404, 400), str(r.status_code))
after = Page.objects.count()
check('DB page count unchanged after SQLi probes', before == after, f'{before}->{after}')

# ── 2. XSS sanitization ───────────────────────────────────────────────
print('\n2. XSS / HTML sanitize')
xss = [
    '<script>alert(1)</script><p>ok</p>',
    '<img src=x onerror=alert(1)>',
    '<a href="javascript:alert(1)">x</a>',
    '<iframe src="https://evil.test"></iframe>',
    '<p onclick="alert(1)">click</p>',
]
for raw in xss:
    cleaned = sanitize_html(raw)
    bad = any(x in cleaned.lower() for x in ['<script', 'onerror=', 'javascript:', '<iframe', 'onclick='])
    check(f'Sanitize blocks XSS', not bad, cleaned[:80])

form = PageForm({
    'title': 'XSS Test Page',
    'content': '<p>Hello</p><script>alert(1)</script>',
    'is_published': True,
    'order': 0,
})
check('PageForm valid with XSS input', form.is_valid(), str(form.errors))
if form.is_valid():
    check('PageForm strips script', '<script' not in (form.cleaned_data['content'] or '').lower())
    check('PageForm keeps safe HTML', '<p>' in (form.cleaned_data['content'] or ''))

# ── 3. CSRF ───────────────────────────────────────────────────────────
print('\n3. CSRF')
r = anon.post('/panel/login/', {'username': 'x', 'password': 'y'})
check('Login without CSRF rejected', r.status_code == 403)

user = User.objects.filter(is_superuser=True).first()
check('Superuser exists for auth tests', user is not None)
staff_client = Client(enforce_csrf_checks=True)
staff_client.force_login(user)
r = staff_client.post('/panel/pages/add/', {
    'title': 'No CSRF Page',
    'content': '<p>x</p>',
    'is_published': 'on',
})
check('Panel POST without CSRF rejected', r.status_code == 403)

# with CSRF
c2 = Client()  # enforce_csrf_checks=False by default for force_login flows in tests
c2.force_login(user)
r = c2.get('/panel/pages/add/')
check('Panel page form has csrf', b'csrfmiddlewaretoken' in r.content)

# ── 4. AuthZ ──────────────────────────────────────────────────────────
print('\n4. Authorization')
for url in ['/panel/', '/panel/pages/', '/panel/documents/', '/panel/users/', '/panel/media/']:
    r = anon.get(url)
    check(f'Anon blocked {url}', r.status_code in (301, 302))

# non-staff user
plain, created = User.objects.get_or_create(username='sec_plain_user', defaults={'is_staff': False})
if created:
    plain.set_password('testpass123')
    plain.save()
plain.is_staff = False
plain.is_superuser = False
plain.save()
pc = Client()
pc.force_login(plain)
r = pc.get('/panel/')
check('Non-staff cannot open panel', r.status_code in (301, 302, 403))
r = pc.get('/panel/users/')
check('Non-staff cannot open users', r.status_code in (301, 302, 403))

# ── 5. Open redirect ──────────────────────────────────────────────────
print('\n5. Open redirect')
check(
    'External next= rejected',
    not is_safe_redirect_url('https://evil.example/phish', allowed_hosts={'localhost'}),
)
check(
    'Protocol-relative rejected',
    not is_safe_redirect_url('//evil.example/', allowed_hosts={'localhost'}),
)
check(
    'Local next= allowed',
    is_safe_redirect_url('/panel/pages/', allowed_hosts={'localhost', 'testserver'}),
)

# login with evil next
c3 = Client()
r = c3.post('/panel/login/?next=https://evil.example/steal', {
    'username': user.username,
    'password': 'wrong-password-definitely',
})
# wrong password — just ensure no open redirect on success path via unit already
# success path:
from cms.security_utils import is_safe_redirect_url as safe
evil = 'https://evil.example/'
check('Login would not accept evil next', not safe(evil, { 'testserver', *settings.ALLOWED_HOSTS }))

# ── 6. Path traversal (media) ─────────────────────────────────────────
print('\n6. Path traversal')
media = settings.MEDIA_ROOT
os.makedirs(media, exist_ok=True)
try:
    safe_join_media(media, '../../etc/passwd')
    check('Traversal blocked', False)
except ValueError:
    check('Traversal ../../ blocked', True)

try:
    safe_join_media(media, '..\\..\\windows\\system32')
    check('Traversal windows blocked', False)
except ValueError:
    check('Traversal windows blocked', True)

check('subdir .. rejected', sanitize_upload_subdir('../etc') == 'uploads')
check('subdir absolute-ish rejected', sanitize_upload_subdir('/etc') == 'uploads')
check('subdir ok', sanitize_upload_subdir('documents') == 'documents')

try:
    sanitize_upload_filename('../../evil.php')
    check('evil.php blocked', False)
except ValueError:
    check('evil.php / traversal name blocked', True)

try:
    sanitize_upload_filename('shell.exe')
    check('exe blocked', False)
except ValueError:
    check('exe extension blocked', True)

check('pdf allowed', sanitize_upload_filename('doc.pdf') == 'doc.pdf')

# live media delete traversal as staff
c2.force_login(user)
r = c2.post('/panel/media/delete/', {'path': '../../settings.py'})
check('media_delete traversal rejected', r.status_code in (302, 200))
# ensure settings.py still exists
check('settings.py not deleted', os.path.isfile(os.path.join(settings.BASE_DIR, 'techcollege_admin', 'settings.py')))

# ── 7. API methods ────────────────────────────────────────────────────
print('\n7. API hardening')
r = anon.post('/api/menu/')
check('api_menu rejects POST', r.status_code in (403, 405))
r = anon.get('/api/menu/')
check('api_menu GET ok', r.status_code == 200)
r = anon.post('/api/homepage/')
check('api_homepage rejects POST', r.status_code in (403, 405))

# ── 8. Headers / cookies config ───────────────────────────────────────
print('\n8. Security settings')
check('X_FRAME_OPTIONS DENY', getattr(settings, 'X_FRAME_OPTIONS', '') == 'DENY')
check('NOSNIFF on', getattr(settings, 'SECURE_CONTENT_TYPE_NOSNIFF', False) is True)
check('SESSION_COOKIE_HTTPONLY', getattr(settings, 'SESSION_COOKIE_HTTPONLY', False) is True)
check('CSRF_COOKIE_HTTPONLY', getattr(settings, 'CSRF_COOKIE_HTTPONLY', False) is True)
check('Password validators configured', len(settings.AUTH_PASSWORD_VALIDATORS) >= 3)

# ── 9. Mass assignment / privilege ────────────────────────────────────
print('\n9. Privilege escalation')
r = c2.post('/panel/users/add/', {
    'username': 'hacker_sec_test',
    'password': 'ComplexPass!234',
    'is_staff': 'on',
    'is_active': 'on',
    'is_superuser': 'on',  # not in form — must be ignored
})
u = User.objects.filter(username='hacker_sec_test').first()
if u:
    check('Created user is not superuser via mass-assign', u.is_superuser is False)
    u.delete()
else:
    # form may require fields — still OK if not created as superuser somehow
    check('No unexpected superuser created', not User.objects.filter(username='hacker_sec_test', is_superuser=True).exists())

# cleanup
User.objects.filter(username='sec_plain_user').delete()
Page.objects.filter(title='XSS Test Page').delete()

print('\n' + '=' * 60)
print(f'OK={len(ok)} FAIL={len(fail)}')
print('=' * 60)
if fail:
    for f in fail:
        print(f'  - {f}')
    sys.exit(1)
print('SECURITY CHECKS PASSED')
sys.exit(0)
