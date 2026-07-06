@echo off
chcp 65001 >nul
echo ========================================
echo Установка Django CMS для Техникума
echo ========================================
echo.

echo [1/6] Установка зависимостей...
pip install -r requirements.txt
pip install requests
if errorlevel 1 (
    echo Ошибка при установке зависимостей!
    echo Попробуйте: python -m pip install --upgrade pip
    pause
    exit /b 1
)
echo ✓ Зависимости установлены
echo.

echo [2/6] Создание миграций...
python manage.py makemigrations
if errorlevel 1 (
    echo Ошибка при создании миграций!
    pause
    exit /b 1
)
echo ✓ Миграции созданы
echo.

echo [3/6] Применение миграций...
python manage.py migrate
if errorlevel 1 (
    echo Ошибка при применении миграций!
    pause
    exit /b 1
)
echo ✓ База данных создана
echo.

echo [4/6] Создание начальных данных...
python manage.py create_initial_data
echo ✓ Начальные данные созданы
echo.

echo [5/6] Создание суперпользователя...
echo.
echo Введите данные для администратора:
echo (Username: admin, Email: admin@kktbel.ru)
echo.
python manage.py createsuperuser
echo.

echo [6/6] Импорт документов из JSON...
python manage.py import_all_documents
echo ✓ Документы импортированы
echo.

echo ========================================
echo ✓ Установка завершена успешно!
echo ========================================
echo.
echo Что дальше:
echo 1. Запустите сервер: run.bat
echo 2. Откройте сайт: http://localhost:8000/
echo 3. Откройте админку: http://localhost:8000/admin/
echo 4. Войдите с созданным логином и паролем
echo 5. Начните редактировать контент!
echo.
echo Для проверки работы API запустите:
echo python test_api.py
echo.
pause
