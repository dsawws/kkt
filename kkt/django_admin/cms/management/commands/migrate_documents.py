from django.core.management.base import BaseCommand
from django.core.files import File
from cms.models import Document, Page
import os
import shutil
import json


class Command(BaseCommand):
    help = 'Миграция документов из старого сайта'

    def handle(self, *args, **options):
        self.stdout.write('Начало миграции документов...')
        
        # Путь к старым документам
        base_path = '../frontend/pages/abiturient/pdf/'
        
        # Получаем страницу "Поступающим"
        try:
            page = Page.objects.get(slug='abiturient')
        except Page.DoesNotExist:
            self.stdout.write(self.style.ERROR('Страница "Поступающим" не найдена. Сначала запустите create_initial_data'))
            return
        
        # Категории документов и их папки
        categories_map = {
            'Dokumenti': ('dokumenti', 'Документы'),
            'Informatsiya_postupayushchim': ('informatsiya_postupayushchim', 'Информация поступающим'),
            'Obrazovanie_invalidov': ('obrazovanie_invalidov', 'Образование инвалидов'),
            'Obshchezhitie': ('obshchezhitie', 'Общежитие'),
            'Prikazi_o_zachislenii': ('prikazi_o_zachislenii', 'Приказы о зачислении'),
            'Spiski_postupayushchikh': ('spiski_postupayushchikh', 'Списки поступающих'),
            'Usloviya_priyoma': ('usloviya_priyoma', 'Условия приёма'),
            'Zayavlenie_o_priyome_i_dogovor': ('zayavlenie_o_priyome_i_dogovor', 'Заявление о приёме и договор'),
        }
        
        total_migrated = 0
        
        for folder, (category_code, category_name) in categories_map.items():
            folder_path = os.path.join(base_path, folder)
            
            if not os.path.exists(folder_path):
                self.stdout.write(self.style.WARNING(f'Папка не найдена: {folder_path}'))
                continue
            
            self.stdout.write(f'\nОбработка категории: {category_name}')
            
            # Получаем список файлов
            files = [f for f in os.listdir(folder_path) if f.endswith('.pdf')]
            
            for idx, filename in enumerate(files, 1):
                # Проверяем, не существует ли уже такой документ
                title = filename.replace('.pdf', '').replace('-', ' ').replace('_', ' ')
                
                if Document.objects.filter(title=title, page=page).exists():
                    self.stdout.write(f'  ⊘ Пропущен (уже существует): {title}')
                    continue
                
                # Создаем документ
                doc = Document(
                    page=page,
                    category=category_code,
                    title=title,
                    order=idx,
                    is_active=True
                )
                
                # Копируем файл
                old_file_path = os.path.join(folder_path, filename)
                try:
                    with open(old_file_path, 'rb') as f:
                        doc.file.save(filename, File(f), save=True)
                    
                    total_migrated += 1
                    self.stdout.write(self.style.SUCCESS(f'  ✓ {title}'))
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f'  ✗ Ошибка при копировании {filename}: {str(e)}'))
        
        self.stdout.write(self.style.SUCCESS(f'\n✓ Миграция завершена! Перенесено документов: {total_migrated}'))
