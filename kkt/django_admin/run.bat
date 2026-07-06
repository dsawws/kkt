@echo off
chcp 65001 >nul
echo ========================================
echo Запуск Django CMS для Техникума
echo ========================================
echo.
echo Сервер будет доступен по адресу:
echo http://localhost:8001/
echo.
echo Админ-панель:
echo http://localhost:8001/admin/
echo.
echo Для остановки нажмите Ctrl+C
echo.
py manage.py runserver 0.0.0.0:8001
