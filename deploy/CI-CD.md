# Подробная инструкция: CI/CD для new.kktbel.ru

Документ для тех, кто настраивает автоматические проверки и деплой кнопкой из GitHub.

---

## Что это даёт простыми словами

После настройки:

1. **CI (проверка)** — при каждом push / pull request GitHub сам:
   - ставит зависимости;
   - запускает `manage.py check` и тесты;
   - собирает статику;
   - гоняет smoke- и security-тесты.
   Если что-то сломалось — пайплайн красный, в прод лучше не выкатывать.

2. **Deploy (выкладка)** — **не сам**, а только когда вы нажали кнопку в GitHub:
   - Actions подключается к серверу по SSH;
   - на сервере выполняется `deploy/remote-update.sh`;
   - код обновляется, миграции, collectstatic, перезапуск gunicorn;
   - проверяется, что сайт и статика отвечают.

Сайт: **https://new.kktbel.ru**  
Код на сервере обычно лежит в: **`/var/www/html`**

---

## Что нужно заранее

| Что | Зачем |
|-----|--------|
| Репозиторий на **GitHub** с этими файлами (`.github/workflows/…`, `deploy/…`) | CI и Deploy живут в Actions |
| VPS, куда уже (или скоро) ставится Django | Цель деплоя |
| Доступ по **SSH** на сервер | Deploy ходит по SSH |
| Права написать Secrets в настройках репозитория | Ключи не кладём в код |

Файлы в проекте:

| Файл | Роль |
|------|------|
| `.github/workflows/ci.yml` | Автопроверки |
| `.github/workflows/deploy.yml` | Деплой по кнопке |
| `deploy/remote-update.sh` | Скрипт обновления **на сервере** |
| `deploy/collectstatic.sh` | Сборка статики |
| `deploy/kktbel.service` | systemd (gunicorn) |
| `deploy/kktbel.env.example` | Шаблон секретов для сервера |
| `.env.example` | Список переменных (для ориентира) |

---

## Часть 1. Код в GitHub

Локальная папка проекта должна быть связана с GitHub-репозиторием.

Если репозиторий уже есть — закоммитьте и запушьте ветку `main` (или `master`):

```bash
git add .github deploy .env.example README.md .gitignore
git commit -m "Add CI and button deploy for new.kktbel.ru"
git push origin main
```

После push откройте репозиторий → вкладка **Actions**.  
Должны появиться workflows **CI** и **Deploy**.

---

## Часть 2. Сервер (один раз)

Делается **на VPS** под root или через sudo. Цель — чтобы сайт уже работал и `remote-update.sh` мог его обновлять.

### 2.1. Репозиторий на сервере — именно git clone

Каталог `/var/www/html` должен быть **клоном** того же GitHub-репозитория, а не просто скопированными файлами без `.git`.

Проверка:

```bash
cd /var/www/html
git status
git remote -v
```

Если это не clone — перенесите сайт и сделайте clone (или `git init` + `remote add` + pull — аккуратно с media/sqlite).

### 2.2. Python venv и зависимости

```bash
cd /var/www/html/django_admin
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 2.3. Секреты Django — файл `/etc/kktbel.env`

```bash
sudo cp /var/www/html/deploy/kktbel.env.example /etc/kktbel.env
sudo chmod 600 /etc/kktbel.env
sudo nano /etc/kktbel.env
```

Внутри обязательно замените:

```text
DJANGO_SECRET_KEY=замените-на-длинную-случайную-строку
```

на длинный случайный ключ (не коммитьте этот файл).

Остальное обычно так:

```text
DJANGO_DEBUG=0
DJANGO_ALLOWED_HOSTS=new.kktbel.ru,kktbel.ru,www.kktbel.ru,127.0.0.1
DJANGO_CSRF_TRUSTED_ORIGINS=https://new.kktbel.ru,https://kktbel.ru,https://www.kktbel.ru
DJANGO_SETTINGS_MODULE=techcollege_admin.settings
```

### 2.4. Миграции, статика, админ (если ещё не делали)

```bash
cd /var/www/html/django_admin
source venv/bin/activate
set -a && source /etc/kktbel.env && set +a
export DJANGO_DEBUG=0

python manage.py migrate
bash /var/www/html/deploy/collectstatic.sh
python manage.py createsuperuser   # если админа ещё нет
```

### 2.5. systemd (gunicorn)

```bash
sudo cp /var/www/html/deploy/kktbel.service /etc/systemd/system/kktbel.service
sudo systemctl daemon-reload
sudo systemctl enable --now kktbel
sudo systemctl status kktbel
```

В unit уже есть `EnvironmentFile=-/etc/kktbel.env`.

### 2.6. Nginx

Как в `deploy/README.md`: конфиг `nginx-new.kktbel.ru.conf` → sites-available → `nginx -t` → reload.

Проверка в браузере: https://new.kktbel.ru/

### 2.7. Пользователь для деплоя по SSH

Не обязательно root. Удобно завести пользователя, например `deploy`:

```bash
sudo adduser deploy
sudo mkdir -p /home/deploy/.ssh
sudo chmod 700 /home/deploy/.ssh
```

**На своём компьютере** сгенерируйте ключ (если ещё нет отдельного для деплоя):

```bash
ssh-keygen -t ed25519 -C "github-deploy-kktbel" -f ./kktbel_deploy_ed25519 -N ""
```

Получится:

- `kktbel_deploy_ed25519` — **приватный** (пойдёт в GitHub Secret, никому не светить);
- `kktbel_deploy_ed25519.pub` — **публичный** (на сервер).

На сервере:

```bash
# вставить содержимое .pub в authorized_keys
sudo nano /home/deploy/.ssh/authorized_keys
sudo chmod 600 /home/deploy/.ssh/authorized_keys
sudo chown -R deploy:deploy /home/deploy/.ssh
```

Права на код: пользователь `deploy` должен уметь читать/писать `/var/www/html` (git pull / reset).  
Пример (уточните под вашу схему владельцев):

```bash
sudo chown -R deploy:www-data /var/www/html
sudo chmod -R g+rwX /var/www/html
# media часто пишет www-data — не отбирайте запись у gunicorn
sudo chown -R www-data:www-data /var/www/html/django_admin/media
```

Право перезапускать gunicorn без пароля:

```bash
sudo visudo -f /etc/sudoers.d/kktbel-deploy
```

Строка:

```text
deploy ALL=(root) NOPASSWD: /bin/systemctl restart kktbel, /bin/systemctl status kktbel
```

Проверка с вашего ПК:

```bash
ssh -i ./kktbel_deploy_ed25519 deploy@IP_ИЛИ_new.kktbel.ru
cd /var/www/html && bash deploy/remote-update.sh main
```

Если скрипт отработал локально по SSH — кнопка в GitHub сможет то же самое.

---

## Часть 3. Secrets в GitHub

Откройте репозиторий → **Settings** → **Secrets and variables** → **Actions** → **New repository secret**.

Создайте:

| Имя секрета | Что вписать |
|-------------|-------------|
| `DEPLOY_HOST` | IP сервера или `new.kktbel.ru` (куда SSH) |
| `DEPLOY_USER` | например `deploy` |
| `DEPLOY_SSH_KEY` | **весь** текст приватного ключа `kktbel_deploy_ed25519`, включая строки `BEGIN` / `END` |

Опционально:

| Имя | Когда нужно | По умолчанию |
|-----|-------------|--------------|
| `DEPLOY_PORT` | SSH не на 22 порту | `22` |
| `DEPLOY_PATH` | код не в `/var/www/html` | `/var/www/html` |

### Environment `production`

В workflow деплоя указано `environment: production`.

1. **Settings** → **Environments** → **New environment** → имя: `production`.
2. По желанию включите **Required reviewers** — тогда перед выкладкой кто-то должен подтвердить.

Секреты можно повесить на Environment или на репозиторий — оба варианта работают, если имена совпадают.

---

## Часть 4. Как пользоваться каждый день

### Проверки (CI) — сами

1. Пушите код в `main` / `develop` или открываете Pull Request.
2. Вкладка **Actions** → workflow **CI**.
3. Зелёный = можно думать о деплое. Красный = читайте лог упавшего шага.

CI **не меняет** сайт на сервере.

### Выкладка (Deploy) — только кнопка

1. Убедитесь, что нужный код уже в GitHub (в ветке `main` или другой).
2. **Actions** → слева **Deploy** → справа **Run workflow**.
3. Поле **Git-ветка или тег** — обычно `main`.
4. **Run workflow**.
5. Дождитесь зелёного статуса.
6. Откройте https://new.kktbel.ru/ и проверьте панель / статику.

Что происходит на сервере при успехе:

1. `git fetch` + переход на выбранную ветку  
2. `pip install -r requirements.txt`  
3. Бэкап `db.sqlite3` (если есть)  
4. `migrate`  
5. `collectstatic`  
6. `systemctl restart kktbel`  
7. Проверка URL сайта и CSS  

---

## Часть 5. Типичные проблемы

| Симптом | Что проверить |
|---------|----------------|
| CI красный на smoke | Нужны миграции + данные; в CI создаётся `ci_admin` и `create_initial_data` — смотрите полный лог |
| Deploy: Permission denied (publickey) | Неверный `DEPLOY_SSH_KEY` / ключ не в `authorized_keys` / неверный `DEPLOY_USER` |
| Deploy: Host key / ssh-keyscan | Неверный `DEPLOY_HOST` или порт; файрвол режет SSH |
| Deploy: venv not found | На сервере нет `/var/www/html/django_admin/venv` — см. §2.2 |
| Deploy: sudo password / denied | Нет строки в sudoers для `systemctl restart kktbel` |
| Сайт 500 после деплоя | `DJANGO_SECRET_KEY` в `/etc/kktbel.env`; `journalctl -u kktbel -n 50` |
| Статика 404 | `bash deploy/collectstatic.sh`; nginx смотрит только на `staticfiles/` |
| git reset на сервере «стёр» правки | На сервере нельзя править код руками без коммита — правки только через GitHub |

Откат на предыдущий коммит: в Run workflow укажите тег/ветку со старым кодом **или** на сервере:

```bash
cd /var/www/html
git log --oneline -5
bash deploy/remote-update.sh <нужный_коммит_или_тег>
```

(для коммита может понадобиться чуть другой checkout — проще держать теги релизов).

---

## Часть 6. Чеклист «всё готово»

- [ ] Код с `.github/workflows` запушен в GitHub  
- [ ] На сервере `/var/www/html` — git clone этого репо  
- [ ] Есть `django_admin/venv` и зависимости  
- [ ] Есть `/etc/kktbel.env` с настоящим `DJANGO_SECRET_KEY`  
- [ ] Работают systemd `kktbel` и nginx, сайт открывается  
- [ ] Пользователь SSH + ключ + sudo на restart  
- [ ] Вручную один раз: `bash deploy/remote-update.sh main` по SSH  
- [ ] В GitHub заданы `DEPLOY_HOST`, `DEPLOY_USER`, `DEPLOY_SSH_KEY`  
- [ ] Создан Environment `production`  
- [ ] CI зелёный на последнем push  
- [ ] Deploy по кнопке прошёл успешно  

---

## Краткая шпаргалка

```text
Разработка → git push → смотрим CI (Actions)
Всё зелёное → Actions → Deploy → Run workflow → main
Сайт обновился на https://new.kktbel.ru
```

Ручной деплой без GitHub (если Actions недоступен):

```bash
ssh deploy@СЕРВЕР
cd /var/www/html
bash deploy/remote-update.sh main
```
