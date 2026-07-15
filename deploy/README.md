# Деплой static + nginx для new.kktbel.ru
#
# Проблема, которую это решает
# ----------------------------
# Раньше /static/ указывал на 8+ разных папок на диске (frontend, venv/ckeditor,
# venv/mptt, venv/admin, django_admin/static/panel, uploads, …).
# После каждого обновления появлялись новые 404.
#
# Правильная модель Django
# ------------------------
# 1. Исходники статики:
#    - django_admin/static/     — CSS/JS сайта и панели
#    - пакеты (ckeditor, mptt, admin) — через AppDirectoriesFinder
# 2. python manage.py collectstatic → всё в django_admin/staticfiles/
# 3. Nginx отдаёт ТОЛЬКО staticfiles/ по /static/
# 4. /media/ — загруженные пользователями файлы (MEDIA_ROOT)
# 5. /uploads/ — legacy-файлы старого сайта (опционально)
#
# Установка на сервере
# --------------------
# 1. Скопировать репозиторий в /var/www/html/
# 2. Venv + зависимости:
#      cd /var/www/html/django_admin
#      python3 -m venv venv && source venv/bin/activate
#      pip install -r ../requirements.txt gunicorn
# 3. Миграции и статика:
#      export DJANGO_DEBUG=0
#      python manage.py migrate
#      bash ../deploy/collectstatic.sh
# 4. Systemd (порт 8041):
#      bash ../deploy/kktbel.service.example   # посмотреть unit
#      # отредактировать и установить в /etc/systemd/system/kktbel.service
#      sudo systemctl enable --now kktbel
# 5. Nginx:
#      sudo cp ../deploy/nginx-new.kktbel.ru.conf /etc/nginx/sites-available/new.kktbel.ru
#      sudo ln -sf /etc/nginx/sites-available/new.kktbel.ru /etc/nginx/sites-enabled/
#      sudo nginx -t && sudo systemctl reload nginx
#
# После обновления кода или pip install
# -------------------------------------
#   bash /var/www/html/deploy/collectstatic.sh
#   sudo systemctl restart kktbel
#
# Проверка 404
# ------------
#   python manage.py check_static
#   curl -I https://new.kktbel.ru/static/style.css
#   curl -I https://new.kktbel.ru/static/ckeditor/ckeditor/ckeditor.js
#   curl -I https://new.kktbel.ru/static/panel/admin.css
#   curl -I https://new.kktbel.ru/static/admin/css/base.css
