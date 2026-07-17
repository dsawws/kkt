# Деплой static + nginx для new.kktbel.ru

## Модель статики Django

1. Исходники: `django_admin/static/` + пакеты (ckeditor, mptt, admin)
2. `python manage.py collectstatic` → `django_admin/staticfiles/`
3. Nginx отдаёт **только** `staticfiles/` по `/static/`
4. `/media/` — загрузки пользователей (`MEDIA_ROOT`)
5. `/uploads/` — legacy-файлы старого сайта (опционально)

---

## Первичная установка на сервере

1. Клонировать репозиторий в `/var/www/html/` (должен быть **git clone**, не просто zip).
2. Venv + зависимости:

```bash
cd /var/www/html/django_admin
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt
```

3. Секреты:

```bash
sudo cp /var/www/html/deploy/kktbel.env.example /etc/kktbel.env
sudo chmod 600 /etc/kktbel.env
sudo nano /etc/kktbel.env   # задать DJANGO_SECRET_KEY
```

4. Миграции и статика:

```bash
set -a && source /etc/kktbel.env && set +a
export DJANGO_DEBUG=0
python manage.py migrate
bash /var/www/html/deploy/collectstatic.sh
python manage.py createsuperuser   # один раз
```

5. Systemd:

```bash
sudo cp /var/www/html/deploy/kktbel.service /etc/systemd/system/kktbel.service
sudo systemctl daemon-reload
sudo systemctl enable --now kktbel
```

6. Nginx:

```bash
sudo cp /var/www/html/deploy/nginx-new.kktbel.ru.conf /etc/nginx/sites-available/new.kktbel.ru
sudo ln -sf /etc/nginx/sites-available/new.kktbel.ru /etc/nginx/sites-enabled/
sudo nginx -t && sudo systemctl reload nginx
```

7. Права для деплоя по SSH (пример): пользователь `deploy` может писать в `/var/www/html` и перезапускать сервис:

```bash
# /etc/sudoers.d/kktbel-deploy
deploy ALL=(root) NOPASSWD: /bin/systemctl restart kktbel, /bin/systemctl status kktbel
```

Владелец кода: удобно `deploy:www-data` или ACL, чтобы gunicorn (`www-data`) читал файлы, а media писал `www-data`.

---

## Ручное обновление

```bash
bash /var/www/html/deploy/remote-update.sh main
```

Или по шагам: `git pull` → `pip install -r requirements.txt` → backup sqlite → `migrate` → `collectstatic.sh` → `systemctl restart kktbel`.

---

## CI/CD (GitHub Actions)

**Полная пошаговая инструкция (рекомендуется начать с неё):**  
[`deploy/CI-CD.md`](CI-CD.md)

### CI (автоматически)

Файл: [`.github/workflows/ci.yml`](../.github/workflows/ci.yml)

На каждый push/PR в `main` / `develop`:

- `manage.py check`
- `manage.py test cms`
- `collectstatic` + `check_static`
- `smoke_test.py` + `security_test.py`

### Deploy (кнопка)

Файл: [`.github/workflows/deploy.yml`](../.github/workflows/deploy.yml)

**Actions → Deploy → Run workflow** → указать ветку/тег (по умолчанию `main`).

На сервере выполняется `deploy/remote-update.sh`.

#### Secrets репозитория (Settings → Secrets and variables → Actions)

| Secret | Пример | Описание |
|--------|--------|----------|
| `DEPLOY_HOST` | `new.kktbel.ru` или IP | SSH-хост |
| `DEPLOY_USER` | `deploy` | SSH-пользователь |
| `DEPLOY_SSH_KEY` | `-----BEGIN OPENSSH...` | Приватный ключ (без passphrase или с ssh-agent) |
| `DEPLOY_PORT` | `22` | Опционально |
| `DEPLOY_PATH` | `/var/www/html` | Опционально, корень git-репозитория на сервере |

#### Environment `production`

В workflow указан `environment: production`. Создайте Environment в GitHub (Settings → Environments) и при желании включите required reviewers перед деплоем.

#### Первый прогон

1. Убедиться, что на сервере `/var/www/html` — clone того же remote, что в GitHub.
2. Ключ `DEPLOY_SSH_KEY` добавлен в `~/.ssh/authorized_keys` пользователя `DEPLOY_USER`.
3. Локально один раз: `bash deploy/remote-update.sh main` (проверка скрипта).
4. В GitHub: Run workflow.

---

# Проверка документов (не путать со static)
# -----------------------------------------
# Список документов на странице отдаёт Django (БД), не nginx и не collectstatic.
# Файлы PDF открываются через:
#   location /media/ → /var/www/html/django_admin/media/
#
# Проверки на сервере:
#   ls /var/www/html/django_admin/media/documents/
#   curl -I https://new.kktbel.ru/media/documents/.../файл.pdf
#   # в панели: у документа указана нужная Страница + Активен + загружен Файл
#
# Если списка нет на странице — документ привязан к другой странице в панели.
# Если список есть, а «Открыть» = 404 — нет файла в media/ или сломан location /media/.
