#!/usr/bin/env bash
# Сборка единой директории статики для nginx.
# Запускать после каждого деплоя / обновления зависимостей (ckeditor, mptt, …).
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
DJANGO_DIR="${DJANGO_DIR:-$ROOT/django_admin}"
VENV="${VENV:-$DJANGO_DIR/venv}"

cd "$DJANGO_DIR"

if [[ -f "$VENV/bin/activate" ]]; then
  # shellcheck disable=SC1091
  source "$VENV/bin/activate"
fi

export DJANGO_SETTINGS_MODULE="${DJANGO_SETTINGS_MODULE:-techcollege_admin.settings}"

echo "==> collectstatic → $DJANGO_DIR/staticfiles"
python manage.py collectstatic --noinput --clear

echo "==> проверка ключевых путей"
python manage.py check_static

echo "==> готово. Nginx location /static/ → $DJANGO_DIR/staticfiles/"
