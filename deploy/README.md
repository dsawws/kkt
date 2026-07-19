# Деплой: Nginx :8042 → Gunicorn :8041 (new.kktbel.ru)

## Конечная схема (TSO)

| Компонент | Порт / путь | Файл |
|-----------|-------------|------|
| Nginx | HTTP **8042** → бэкенд | `/var/www/html/deploy/nginx-new.kktbel.ru.conf` |
| Gunicorn (бэкенд) | HTTP **8041** | systemd `kktbel` из `/var/www/html/deploy/kktbel.service` |
| Venv | — | `/var/www/html/django_admin/venv` |
| Переменные окружения | — | `/var/www/html/deploy/kktbel.env` (**в .gitignore**) |
| Шаблон env | — | `/var/www/html/deploy/kktbel.env.example` (в Git) |

TLS обычно терминируется **перед** nginx; сам nginx на сервере приложения слушает HTTP :8042.

## Модель статики Django

1. Исходники: `django_admin/static/` + пакеты (ckeditor, mptt, admin)
2. `python manage.py collectstatic` → `django_admin/staticfiles/`
3. Nginx отдаёт **только** `staticfiles/` по `/static/`
4. `/media/` — загрузки пользователей (`MEDIA_ROOT`)
5. `/uploads/` — legacy-файлы старого сайта (опционально)

---

## Первичная установка на сервере

1. Клонировать репозиторий в `/var/www/html/` (**git clone**, не zip).

2. Venv + зависимости:

```bash
cd /var/www/html/django_admin
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt
```

3. Секреты (файл рядом с шаблоном, не в `/etc`):

```bash
cp /var/www/html/deploy/kktbel.env.example /var/www/html/deploy/kktbel.env
chmod 640 /var/www/html/deploy/kktbel.env
chown root:www-data /var/www/html/deploy/kktbel.env
nano /var/www/html/deploy/kktbel.env   # задать DJANGO_SECRET_KEY
```

4. Миграции и статика:

```bash
set -a && source /var/www/html/deploy/kktbel.env && set +a
cd /var/www/html/django_admin
source venv/bin/activate
python manage.py migrate
bash /var/www/html/deploy/collectstatic.sh
python manage.py createsuperuser   # один раз
```

5. Systemd (юнит из репозитория → `/etc/systemd/system/`):

```bash
sudo cp /var/www/html/deploy/kktbel.service /etc/systemd/system/kktbel.service
sudo systemctl daemon-reload
sudo systemctl enable --now kktbel
sudo systemctl status kktbel
```

6. Nginx (конфиг из `deploy/`, listen **8042**):

```bash
sudo cp /var/www/html/deploy/nginx-new.kktbel.ru.conf /etc/nginx/sites-available/new.kktbel.ru
# или include /var/www/html/deploy/nginx-new.kktbel.ru.conf; в http {}
sudo ln -sf /etc/nginx/sites-available/new.kktbel.ru /etc/nginx/sites-enabled/
sudo nginx -t && sudo systemctl reload nginx
```

Проверка локально на сервере: `curl -I http://127.0.0.1:8042/` и `curl -I http://127.0.0.1:8041/` (8041 — только gunicorn).

7. Права для деплоя по SSH (пример):

```bash
# /etc/sudoers.d/kktbel-deploy
deploy ALL=(root) NOPASSWD: /bin/systemctl restart kktbel, /bin/systemctl status kktbel
```

Владелец кода: удобно `deploy:www-data`; `media/` пишет `www-data`.

---

## Ручное обновление

```bash
bash /var/www/html/deploy/remote-update.sh main
```

Скрипт читает `deploy/kktbel.env`, не трогает `media/`.

---

## CI/CD (GitHub Actions)

**Полная инструкция:** [`deploy/CI-CD.md`](CI-CD.md)

Secrets: `DEPLOY_HOST`, `DEPLOY_USER`, `DEPLOY_SSH_KEY`.  
Deploy → SSH → `remote-update.sh` (migrate, collectstatic, restart `kktbel`).

---

## Документы vs static

Список документов отдаёт Django (БД). PDF открываются через `/media/` → `django_admin/media/`.  
`collectstatic` к документам не относится.
