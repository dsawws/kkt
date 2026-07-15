# Сайт Краснодарского кооперативного техникума — Django CMS

## Структура проекта

```
├── django_admin/          # Django бэкенд + CMS
│   ├── cms/               # Приложение: модели, views, admin
│   ├── templates/         # HTML шаблоны (cms/ + panel/)
│   ├── static/            # ИСХОДНИКИ статики (сайт + панель)
│   ├── staticfiles/       # СОБРАННАЯ статика (collectstatic) → nginx /static/
│   ├── media/             # Загрузки пользователей → nginx /media/
│   ├── manage.py
│   └── ...
├── deploy/                # Nginx, systemd, collectstatic.sh
├── frontend/              # Legacy HTML (не источник /static/ для nginx)
└── uploads/               # Legacy файлы → nginx /uploads/
```

---

## Установка и запуск

### Шаг 1 — Установка зависимостей

```bash
cd django_admin
py -m pip install -r requirements.txt
```

### Шаг 2 — Применение миграций

```bash
py manage.py migrate
```

### Шаг 3 — Создание начальных данных (страницы + меню)

```bash
py manage.py create_initial_data
```

Создаёт все страницы из навбара и пункты меню автоматически.

### Шаг 4 — Создание администратора

```bash
py manage.py createsuperuser
```

### Шаг 5 — Запуск сервера

```bash
py manage.py runserver 0.0.0.0:8000
```

Или через `run.bat`.

---

## Адреса

| Адрес | Описание |
|---|---|
| http://localhost:8000/ | Главная страница сайта |
| http://localhost:8000/admin/ | Админ-панель |
| http://localhost:8000/page/basic-info/ | Сведения об организации |
| http://localhost:8000/page/abiturient/ | Поступающим |
| http://localhost:8000/page/student/ | Студентам |
| http://localhost:8000/page/teacher/ | Преподавателям |
| http://localhost:8000/page/professions/ | Специальности |
| http://localhost:8000/page/news/ | Новости |
| http://localhost:8000/page/kredit/ | Обркредит в СПО |
| http://localhost:8000/page/ssk/ | ССК |
| http://localhost:8000/page/antinarko/ | Антинарко |
| http://localhost:8000/page/profilaktika/ | Профилактика |
| http://localhost:8000/api/menu/ | API: меню |
| http://localhost:8000/api/homepage/ | API: главная страница |
| http://localhost:8000/api/page-api/<slug>/ | API: данные страницы |

---

## Работа с админкой

### Главная страница
**Управление контентом → Главная страница**

Поля:
- Заголовок приветствия
- Текст приветствия
- Имя директора, должность, фото
- Обращение директора
- Заголовок слайдера, текст слайдера, изображение слайдера

### Страницы
**Управление контентом → Страницы**

Каждая страница содержит:
- Заголовок и slug (URL)
- Описание
- Основное содержимое (Rich-text редактор с загрузкой изображений)
- Блоки контента (добавляются внизу формы)
- Документы (добавляются внизу формы)
- SEO поля (meta title, description, keywords)
- Флаг "Опубликовано"

### Навигационное меню
**Управление контентом → Навигационное меню**

- Drag & drop для изменения порядка
- Поле "Родительский пункт" — для создания подменю
- Поле "Связанная страница" — привязка к странице
- Флаг "Активен" — показывать/скрывать пункт

Пример создания подменю:
1. Создайте пункт "Документы"
2. В поле "Родительский пункт" выберите "Сведения об организации"
3. Сохраните — "Документы" появится в выпадающем меню

### Загрузка документов
**Управление контентом → Документы**

Или прямо внутри страницы (прокрутите вниз до раздела "Документы").

Поля:
- Страница — к какой странице относится документ
- Категория — группировка на странице:
  - Документы
  - Информация поступающим
  - Образование инвалидов
  - Общежитие
  - Приказы о зачислении
  - Списки поступающих
  - Условия приёма
  - Заявление о приёме и договор
  - Прочее
- Название документа
- Файл (PDF, DOC, XLS, любой формат)
- Порядок отображения
- Флаг "Активен"

Размер файла рассчитывается автоматически.
Документы на странице группируются по категориям автоматически.

### Блоки контента
Внутри страницы → раздел "Блоки контента"

Типы блоков:
- **Текст** — форматированный текст через CKEditor
- **Изображение** — одиночное изображение
- **Галерея** — несколько изображений
- **Видео** — встроенное видео (YouTube, Vimeo — вставьте iframe)
- **HTML** — произвольный HTML код
- **Файл** — ссылка на файл

Поле "Порядок" определяет последовательность отображения блоков.

### Галереи
**Управление контентом → Галереи**

- Создайте галерею, привяжите к странице
- Добавьте изображения внутри галереи
- Управляйте порядком через поле "Порядок"

---

## Миграция документов из старого сайта

Перенести PDF из `frontend/pages/abiturient/pdf/` в Django:

```bash
py manage.py migrate_documents
```

---

## База данных

Файл: `django_admin/db.sqlite3`

Таблицы:
- `cms_menuitem` — пункты навигационного меню
- `cms_page` — страницы сайта
- `cms_contentblock` — блоки контента
- `cms_document` — документы
- `cms_homepage` — настройки главной страницы
- `cms_gallery` — галереи
- `cms_galleryimage` — изображения в галереях

Резервная копия:
```bash
py manage.py dumpdata > backup.json
```

Восстановление:
```bash
py manage.py loaddata backup.json
```

---

## API

Все API endpoints возвращают JSON и доступны без авторизации.

### GET /api/menu/
Возвращает дерево навигационного меню.

```json
[
  {
    "id": 1,
    "title": "Сведения об организации",
    "url": "/page/basic-info/",
    "children": []
  }
]
```

### GET /api/homepage/
Возвращает данные главной страницы.

```json
{
  "welcome_title": "Добро пожаловать!",
  "welcome_text": "...",
  "director_name": "...",
  "director_position": "...",
  "director_image": "/media/homepage/photo.jpg",
  "slider_title": "...",
  "slider_text": "..."
}
```

### GET /api/page-api/<slug>/
Возвращает данные страницы с блоками и документами.

```json
{
  "id": 1,
  "title": "Поступающим",
  "slug": "abiturient",
  "description": "...",
  "content": "<p>...</p>",
  "blocks": [...],
  "documents": [
    {
      "id": 1,
      "category": "usloviya_priyoma",
      "category_display": "Условия приёма",
      "title": "Условия приёма 2025",
      "file_url": "/media/documents/2025/01/file.pdf",
      "file_size": "1.2 МБ"
    }
  ]
}
```

---

## Команды управления

```bash
# Создать начальные данные (страницы + меню)
py manage.py create_initial_data

# Мигрировать документы из старого сайта
py manage.py migrate_documents

# Создать суперпользователя
py manage.py createsuperuser

# Применить миграции
py manage.py migrate

# Создать миграции после изменения моделей
py manage.py makemigrations

# Собрать статику для продакшена (обязательно после pip install / деплоя)
py manage.py collectstatic --noinput
py manage.py check_static
```

---

## Настройка для продакшена (new.kktbel.ru)

### Статика — одна директория, не 8 alias в nginx

Раньше `/static/` указывал на разрозненные папки (`frontend/`, `venv/.../ckeditor`, `panel/`, `uploads/` …).  
Правильная схема Django:

1. Исходники: `django_admin/static/` + пакеты (ckeditor, mptt, admin)
2. `python manage.py collectstatic` → всё в `django_admin/staticfiles/`
3. Nginx отдаёт **только** `staticfiles/` по `/static/`

После каждого деплоя / `pip install`:

```bash
cd /var/www/html/django_admin
source venv/bin/activate
export DJANGO_DEBUG=0
bash ../deploy/collectstatic.sh   # collectstatic + проверка
```

### Nginx

Готовый конфиг в репозитории:

[`deploy/nginx-new.kktbel.ru.conf`](deploy/nginx-new.kktbel.ru.conf)

```bash
sudo cp deploy/nginx-new.kktbel.ru.conf /etc/nginx/sites-available/new.kktbel.ru
sudo ln -sf /etc/nginx/sites-available/new.kktbel.ru /etc/nginx/sites-enabled/
sudo nginx -t && sudo systemctl reload nginx
```

Суть конфига (пути на сервере `/var/www/html/`):

| URL | Диск |
|-----|------|
| `/static/` | `django_admin/staticfiles/` (после collectstatic) |
| `/media/` | `django_admin/media/` |
| `/uploads/` | `uploads/` (legacy) |
| всё остальное | proxy → `127.0.0.1:8041` |

**Не добавляйте** отдельные `location` для ckeditor/mptt/admin/panel — они уже внутри `staticfiles/`.

### Gunicorn (порт 8041)

```bash
sudo cp deploy/kktbel.service /etc/systemd/system/kktbel.service
# задайте DJANGO_SECRET_KEY в unit-файле
sudo systemctl daemon-reload
sudo systemctl enable --now kktbel
```

### Переменные окружения

```bash
export DJANGO_DEBUG=0
export DJANGO_SECRET_KEY='случайная-длинная-строка'
export DJANGO_ALLOWED_HOSTS=new.kktbel.ru,kktbel.ru,www.kktbel.ru
export DJANGO_CSRF_TRUSTED_ORIGINS=https://new.kktbel.ru,http://new.kktbel.ru
```

### Проверка static после деплоя

```bash
python manage.py check_static
curl -I https://new.kktbel.ru/static/style.css
curl -I https://new.kktbel.ru/static/ckeditor/ckeditor/ckeditor.js
curl -I https://new.kktbel.ru/static/panel/admin.css
curl -I https://new.kktbel.ru/static/admin/css/base.css
```

Подробности: [`deploy/README.md`](deploy/README.md)

---

## Частые проблемы

**`py` не найден** — используйте `python` или `python3`

**Порт 8000 занят:**
```bash
py manage.py runserver 0.0.0.0:9000
```

**Не видно изменений** — Ctrl+F5; на проде после правок CSS/JS снова `collectstatic`

**404 на /static/ckeditor/...** — не хватает `collectstatic` после установки пакетов

**Документы не отображаются** — проверьте что документ активен и привязан к странице

**Ошибка при загрузке изображений** — папка `django_admin/media/` должна существовать и быть доступна www-data

