"""
Django settings for techcollege_admin project.

Production: set env vars DJANGO_DEBUG=0, DJANGO_SECRET_KEY, DJANGO_ALLOWED_HOSTS.
Static files: run `python manage.py collectstatic` — nginx serves only STATIC_ROOT.
"""

from pathlib import Path
import os

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.environ.get(
    'DJANGO_SECRET_KEY',
    'django-insecure-change-this-in-production-12345',
)

DEBUG = os.environ.get('DJANGO_DEBUG', '1') == '1'

ALLOWED_HOSTS = [
    h.strip()
    for h in os.environ.get(
        'DJANGO_ALLOWED_HOSTS',
        'localhost,127.0.0.1,testserver,new.kktbel.ru,kktbel.ru,www.kktbel.ru',
    ).split(',')
    if h.strip()
]

CSRF_TRUSTED_ORIGINS = [
    o.strip()
    for o in os.environ.get(
        'DJANGO_CSRF_TRUSTED_ORIGINS',
        'https://new.kktbel.ru,http://new.kktbel.ru,https://kktbel.ru,https://www.kktbel.ru',
    ).split(',')
    if o.strip()
]

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'ckeditor',
    'ckeditor_uploader',
    'mptt',
    'cms',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'techcollege_admin.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'cms.context_processors.site_context',
            ],
        },
    },
]

WSGI_APPLICATION = 'techcollege_admin.wsgi.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

LANGUAGE_CODE = 'ru-ru'
TIME_ZONE = 'Europe/Moscow'
USE_I18N = True
USE_TZ = True

# ── Static & media ────────────────────────────────────────────────────
# Единый источник для nginx: только STATIC_ROOT после collectstatic.
# Не подключайте frontend/ целиком — там HTML/PDF, не статика Django.
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_DIRS = [
    BASE_DIR / 'static',  # panel/ + site CSS/JS/img
]
STATICFILES_FINDERS = [
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',  # ckeditor, mptt, admin
]
STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.StaticFilesStorage'

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Legacy uploads (старые файлы сайта: PDF и т.п.)
UPLOADS_ROOT = BASE_DIR.parent / 'uploads'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

LOGIN_URL = '/panel/login/'
LOGIN_REDIRECT_URL = '/panel/'

# CKEditor — файлы уходят в MEDIA_ROOT/uploads/
CKEDITOR_UPLOAD_PATH = 'uploads/'
CKEDITOR_IMAGE_BACKEND = 'pillow'
CKEDITOR_JQUERY_URL = 'https://ajax.googleapis.com/ajax/libs/jquery/2.2.4/jquery.min.js'
CKEDITOR_RESTRICT_BY_USER = False

CKEDITOR_CONFIGS = {
    'default': {
        'toolbar': 'full',
        'height': 300,
        'width': '100%',
        'versionCheck': False,
        'allowedContent': True,
        'extraAllowedContent': 'div(*)[*]{*}; span(*)[*]{*}; p(*)[*]{*}; a[*]; img[*]; h1 h2 h3 h4 h5 h6[*]',
        'protectedSource': [
            r'<div[^>]*cms-embed-table[^>]*>[\s\S]*?</div>',
            r'\[\[cms-table:[^\]]+\]\]',
        ],
    },
    'contenttable': {
        'toolbar': 'full',
        'height': 520,
        'width': '100%',
        'versionCheck': False,
        'allowedContent': True,
        'extraPlugins': 'tableresize',
        'extraAllowedContent': (
            'div(*)[*]{*}; span(*)[*]{*}; p(*)[*]{*}; a[*]; img[*]{*}(*); '
            'table[*]{*}(*); thead[*]{*}(*); tbody[*]{*}(*); tfoot[*]{*}(*); '
            'tr[*]{*}(*); th[*]{*}(*); td[*]{*}(*); '
            'h1 h2 h3 h4 h5 h6[*]'
        ),
        'contentsCss': ['/static/panel/ckeditor-table-contents.css'],
        'protectedSource': [
            r'<div[^>]*cms-embed-table[^>]*>[\s\S]*?</div>',
            r'\[\[cms-table:[^\]]+\]\]',
        ],
    },
}

SILENCED_SYSTEM_CHECKS = ['ckeditor.W001']
DATA_UPLOAD_MAX_NUMBER_FIELDS = 20000
FILE_UPLOAD_MAX_MEMORY_SIZE = 10 * 1024 * 1024  # 10 MB
DATA_UPLOAD_MAX_MEMORY_SIZE = 12 * 1024 * 1024

# Заголовки безопасности (SecurityMiddleware)
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'
SESSION_COOKIE_HTTPONLY = True
CSRF_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = 'Lax'
CSRF_COOKIE_SAMESITE = 'Lax'

if not DEBUG:
    if not SECRET_KEY or SECRET_KEY.startswith('django-insecure-'):
        raise RuntimeError(
            'DJANGO_SECRET_KEY must be set to a strong random value when DEBUG=0'
        )
    # Nginx → gunicorn: X-Forwarded-Proto=https (см. deploy/nginx-*.conf)
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
    SESSION_COOKIE_SECURE = os.environ.get('DJANGO_SESSION_COOKIE_SECURE', '1') == '1'
    CSRF_COOKIE_SECURE = os.environ.get('DJANGO_CSRF_COOKIE_SECURE', '1') == '1'
    # Сайт на HTTPS: редирект HTTP→HTTPS (nginx тоже редиректит — дублирование безопасно)
    SECURE_SSL_REDIRECT = os.environ.get('DJANGO_SECURE_SSL_REDIRECT', '1') == '1'
    # HSTS (включать только когда HTTPS стабильно работает)
    SECURE_HSTS_SECONDS = int(os.environ.get('DJANGO_SECURE_HSTS_SECONDS', '31536000'))
    SECURE_HSTS_INCLUDE_SUBDOMAINS = (
        os.environ.get('DJANGO_SECURE_HSTS_INCLUDE_SUBDOMAINS', '0') == '1'
    )
    SECURE_HSTS_PRELOAD = os.environ.get('DJANGO_SECURE_HSTS_PRELOAD', '0') == '1'
    SECURE_REFERRER_POLICY = 'same-origin'
