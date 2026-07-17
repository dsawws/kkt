#!/usr/bin/env bash
# Обновление кода на сервере new.kktbel.ru.
# Запуск из корня репозитория (обычно /var/www/html):
#   bash deploy/remote-update.sh [ref]
# ref по умолчанию: main
#
# Требования:
#   - каталог — git clone этого репозитория
#   - django_admin/venv уже создан
#   - /etc/kktbel.env с DJANGO_SECRET_KEY (для DEBUG=0)
#   - у пользователя есть право: sudo systemctl restart kktbel
set -euo pipefail

REF="${1:-main}"
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
DJANGO_DIR="${DJANGO_DIR:-$ROOT/django_admin}"
VENV="${VENV:-$DJANGO_DIR/venv}"
SITE_URL="${SITE_URL:-https://new.kktbel.ru}"

cd "$ROOT"

echo "==> git fetch / checkout $REF"
git fetch --prune origin
git checkout "$REF"
git reset --hard "origin/$REF"

cd "$DJANGO_DIR"

if [[ ! -x "$VENV/bin/python" ]]; then
  echo "ERROR: venv not found at $VENV — create it first (see deploy/README.md)" >&2
  exit 1
fi

# shellcheck disable=SC1091
source "$VENV/bin/activate"

echo "==> pip install"
pip install -q -r requirements.txt

if [[ -f db.sqlite3 ]]; then
  BAK="db.sqlite3.bak.$(date +%Y%m%d-%H%M%S)"
  echo "==> backup SQLite → $BAK"
  cp -a db.sqlite3 "$BAK"
fi

# Подтянуть env с сервера, если есть (для migrate при DEBUG=0)
if [[ -f /etc/kktbel.env ]]; then
  set -a
  # shellcheck disable=SC1091
  source /etc/kktbel.env
  set +a
fi
export DJANGO_DEBUG="${DJANGO_DEBUG:-0}"
export DJANGO_SETTINGS_MODULE="${DJANGO_SETTINGS_MODULE:-techcollege_admin.settings}"

echo "==> migrate"
python manage.py migrate --noinput

echo "==> collectstatic"
bash "$ROOT/deploy/collectstatic.sh"

echo "==> restart gunicorn"
sudo systemctl restart kktbel

echo "==> health checks"
sleep 2
curl -fsS -o /dev/null -I "${SITE_URL}/" || {
  echo "WARN: site root check failed" >&2
}
curl -fsS -o /dev/null -I "${SITE_URL}/static/style.css"
curl -fsS -o /dev/null -I "${SITE_URL}/static/panel/admin.css"
curl -fsS -o /dev/null -I "${SITE_URL}/static/ckeditor/ckeditor/ckeditor.js"

echo "==> deploy OK ($REF)"
