"""
Проверка, что после collectstatic все нужные файлы лежат в STATIC_ROOT.

  python manage.py check_static
"""

from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError


REQUIRED = [
    # Сайт
    'style.css',
    'media-styles.css',
    'script.js',
    'vk-widget.js',
    'css/responsive.css',
    'img/logo.png',
    'img/VOV.jpg',
    # Панель
    'panel/admin.css',
    'panel/slugify.js',
    'panel/editor-tools.js',
    'panel/table-editor.js',
    # Пакеты (AppDirectoriesFinder → collectstatic)
    'ckeditor/ckeditor/ckeditor.js',
    'admin/css/base.css',
]


class Command(BaseCommand):
    help = 'Проверяет наличие ключевых файлов в STATIC_ROOT после collectstatic'

    def handle(self, *args, **options):
        root = Path(settings.STATIC_ROOT)
        if not root.is_dir():
            raise CommandError(
                f'STATIC_ROOT не существует: {root}\n'
                f'Сначала: python manage.py collectstatic --noinput'
            )

        missing = []
        for rel in REQUIRED:
            if not (root / rel).is_file():
                missing.append(rel)

        # CKEditor uploader (может отличаться по версии)
        uploader_ok = any(root.glob('ckeditor/ckeditor_uploader/**/*')) or (
            root / 'ckeditor' / 'ckeditor_uploader'
        ).exists()

        self.stdout.write(f'STATIC_ROOT: {root}')
        self.stdout.write(f'Файлов всего: {sum(1 for _ in root.rglob("*") if _.is_file())}')

        if missing:
            self.stdout.write(self.style.ERROR('Отсутствуют:'))
            for m in missing:
                self.stdout.write(f'  - {m}')
            raise CommandError(
                'collectstatic неполный. Проверьте STATICFILES_DIRS и установленные пакеты.'
            )

        if not uploader_ok:
            self.stdout.write(self.style.WARNING(
                'Предупреждение: ckeditor_uploader static не найден (проверьте django-ckeditor)'
            ))

        # Показать топ-уровневые каталоги — для отладки nginx alias
        self.stdout.write(self.style.SUCCESS('OK — ключевые static-файлы на месте'))
        self.stdout.write('Каталоги в STATIC_ROOT:')
        for p in sorted(root.iterdir()):
            kind = 'dir' if p.is_dir() else 'file'
            self.stdout.write(f'  [{kind}] {p.name}')
