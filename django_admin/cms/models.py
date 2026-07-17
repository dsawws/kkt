from django.db import models
from django.utils.text import slugify
from mptt.models import MPTTModel, TreeForeignKey
from ckeditor_uploader.fields import RichTextUploadingField


class MenuItem(MPTTModel):
    """Элемент навигационного меню"""
    title = models.CharField('Название', max_length=200)
    slug = models.SlugField('URL', max_length=200, unique=True, blank=True)
    parent = TreeForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='children',
        verbose_name='Родительский пункт'
    )
    page = models.OneToOneField(
        'Page',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='menu_item',
        verbose_name='Связанная страница'
    )
    order = models.IntegerField('Порядок', default=0)
    is_active = models.BooleanField('Активен', default=True)
    created_at = models.DateTimeField('Создано', auto_now_add=True)
    updated_at = models.DateTimeField('Обновлено', auto_now=True)

    class MPTTMeta:
        order_insertion_by = ['order']

    class Meta:
        verbose_name = 'Пункт меню'
        verbose_name_plural = 'Навигационное меню'
        ordering = ['order', 'title']

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title, allow_unicode=True)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        # У разделов вроде «Сведения об организации» своя страница часто пустая —
        # контент/таблицы лежат у детей. Ведём на первого активного ребёнка.
        children = self.get_children().filter(is_active=True).order_by('order', 'title')
        for child in children:
            if child.page_id:
                return child.page.get_absolute_url()
            if child.slug:
                return self._url_for_slug(child.slug)
        if self.page_id:
            return self.page.get_absolute_url()
        if self.slug:
            return self._url_for_slug(self.slug)
        return '#'

    @staticmethod
    def _url_for_slug(slug):
        # Лента новостей — отдельный раздел /news/, не CMS-страница
        if slug in ('news', 'novosti', 'novosti-test'):
            return '/news/'
        return f'/page/{slug}/'

    def get_active_children(self):
        return self.get_children().filter(is_active=True).order_by('order', 'title')


class Page(models.Model):
    """Страница сайта"""
    title = models.CharField('Заголовок', max_length=200)
    slug = models.SlugField('URL', max_length=200, unique=True, blank=True)
    description = models.TextField('Описание', blank=True)
    content = RichTextUploadingField('Содержимое', blank=True)
    order = models.IntegerField('Порядок', default=0)
    parent = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='subpages',
        verbose_name='Родительская страница'
    )
    
    is_published = models.BooleanField('Опубликовано', default=True)
    show_in_menu = models.BooleanField('Показывать в меню', default=False)
    
    meta_title = models.CharField('Meta Title', max_length=200, blank=True)
    meta_description = models.TextField('Meta Description', blank=True)
    meta_keywords = models.CharField('Meta Keywords', max_length=200, blank=True)
    
    created_at = models.DateTimeField('Создано', auto_now_add=True)
    updated_at = models.DateTimeField('Обновлено', auto_now=True)

    class Meta:
        verbose_name = 'Страница'
        verbose_name_plural = 'Страницы'
        ordering = ['-created_at']

    def __str__(self):
        if self.parent:
            return f'{self.parent.title} → {self.title}'
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title, allow_unicode=True)
        if not self.meta_title:
            self.meta_title = self.title
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        if self.slug == 'news':
            return '/news/'
        return f'/page/{self.slug}/'


class ContentBlock(models.Model):
    """Блок контента на странице"""
    BLOCK_TYPES = [
        ('text', 'Текст'),
        ('image', 'Изображение'),
        ('gallery', 'Галерея'),
        ('video', 'Видео'),
        ('file', 'Файл'),
        ('html', 'HTML'),
    ]

    page = models.ForeignKey(
        Page,
        on_delete=models.CASCADE,
        related_name='blocks',
        verbose_name='Страница'
    )
    block_type = models.CharField('Тип блока', max_length=20, choices=BLOCK_TYPES)
    title = models.CharField('Заголовок', max_length=200, blank=True)
    content = RichTextUploadingField('Содержимое', blank=True)
    order = models.IntegerField('Порядок', default=0)
    is_active = models.BooleanField('Активен', default=True)
    
    created_at = models.DateTimeField('Создано', auto_now_add=True)
    updated_at = models.DateTimeField('Обновлено', auto_now=True)

    class Meta:
        verbose_name = 'Блок контента'
        verbose_name_plural = 'Блоки контента'
        ordering = ['order', 'created_at']

    def __str__(self):
        return f'{self.page.title} - {self.get_block_type_display()} ({self.order})'


class DocumentSection(models.Model):
    """Раздел документов — управляет порядком категорий на странице"""
    page = models.ForeignKey(
        Page,
        on_delete=models.CASCADE,
        related_name='document_sections',
        verbose_name='Страница'
    )
    category = models.CharField('Категория', max_length=100)
    title = models.CharField('Заголовок раздела', max_length=200)
    order = models.IntegerField('Порядок', default=0)
    is_active = models.BooleanField('Активен', default=True)

    class Meta:
        verbose_name = 'Раздел документов'
        verbose_name_plural = 'Разделы документов'
        ordering = ['order', 'title']
        unique_together = [('page', 'category')]

    def __str__(self):
        return f'{self.page.title} → {self.title} (порядок: {self.order})'


class Document(models.Model):
    """Документ для загрузки"""
    CATEGORY_CHOICES = [
        # Поступающим
        ('dokumenti', 'Документы'),
        ('informatsiya_postupayushchim', 'Информация поступающим'),
        ('obrazovanie_invalidov', 'Образование инвалидов'),
        ('obshchezhitie', 'Общежитие'),
        ('prikazi_o_zachislenii', 'Приказы о зачислении'),
        ('spiski_postupayushchikh', 'Списки поступающих'),
        ('usloviya_priyoma', 'Условия приёма'),
        ('zayavlenie_o_priyome_i_dogovor', 'Заявление о приёме и договор'),
        # Сведения об организации
        ('osnovnye_svedeniya', 'Основные сведения'),
        ('dokumenty_i_licenzii', 'Документы и лицензии'),
        ('obrazovanie', 'Образование'),
        ('rukovodstvo', 'Руководство'),
        ('pedagogicheskiy_sostav', 'Педагогический состав'),
        ('materialno_tekhnicheskoe', 'Материально-техническое обеспечение'),
        ('platnye_uslugi', 'Платные образовательные услуги'),
        ('finansovo_khozyaystvennaya', 'Финансово-хозяйственная деятельность'),
        ('vakantnyye_mesta', 'Вакантные места'),
        ('stipendii', 'Стипендии и меры поддержки'),
        ('mezhdunarodnoe', 'Международное сотрудничество'),
        ('organizatsiya_pitaniya', 'Организация питания'),
        ('obrazovatelnye_standarty', 'Образовательные стандарты'),
        # Преподавателям
        ('pedagogicheskiy_sostav', 'Педагогический состав'),
        ('attestatsiya', 'Аттестация педагогических работников'),
        ('metodicheskiy_kabinet', 'Методический кабинет'),
        ('konferentsiya', 'Студенческая научно-практическая конференция'),
        # Студентам
        ('student_docs', 'Документы студентам'),
        # Трудоустройство
        ('trudoustrojstvo_docs', 'Трудоустройство'),
        # ССК
        ('ssk_docs', 'Документы ССК'),
        # Антинарко
        ('antinarko_docs', 'Антинарко'),
        # Антикоррупция
        ('antikorrupciya_docs', 'Антикоррупция'),
        # Профилактика
        ('profilaktika_docs', 'Профилактика'),
        ('other', 'Прочее'),
    ]

    page = models.ForeignKey(
        Page,
        on_delete=models.CASCADE,
        related_name='documents',
        verbose_name='Страница',
        null=True,
        blank=True
    )
    category = models.CharField('Категория', max_length=100, choices=CATEGORY_CHOICES, default='other')
    title = models.CharField('Название', max_length=200)
    description = models.TextField('Описание', blank=True)
    external_url = models.URLField('Внешняя ссылка', blank=True)
    file = models.FileField('Файл',upload_to='documents/%Y/%m/',blank=True,null=True)
    file_size = models.CharField('Размер файла', max_length=50, blank=True)
    
    order = models.IntegerField('Порядок', default=0)
    is_active = models.BooleanField('Активен', default=True)
    
    created_at = models.DateTimeField('Создано', auto_now_add=True)
    updated_at = models.DateTimeField('Обновлено', auto_now=True)

    class Meta:
        verbose_name = 'Документ'
        verbose_name_plural = 'Документы'
        ordering = ['category', 'order', 'title']

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if self.file and not self.file_size:
            size = self.file.size
            if size < 1024:
                self.file_size = f'{size} Б'
            elif size < 1024 * 1024:
                self.file_size = f'{size / 1024:.1f} КБ'
            else:
                self.file_size = f'{size / (1024 * 1024):.1f} МБ'
        super().save(*args, **kwargs)


class HomePage(models.Model):
    """Настройки главной страницы"""
    site_name = models.CharField(
        'Название техникума',
        max_length=300,
        default='АНЧ ПОО «Краснодарский кооперативный техникум крайпотребсоюза»',
    )
    site_tagline = models.CharField('Слоган', max_length=200, default='Качество + Креатив + Творчество', blank=True)
    site_phone = models.CharField('Телефон', max_length=50, default='8(86155)2-27-83', blank=True)
    site_email = models.EmailField('Email', default='kktbel@mail.ru', blank=True)
    site_vk = models.URLField('ВКонтакте', default='https://vk.com/belkkt', blank=True)
    site_telegram = models.URLField('Telegram', default='https://t.me/belkkt', blank=True)

    welcome_title = models.CharField('Заголовок приветствия', max_length=200, default='Добро пожаловать!')
    welcome_text = models.TextField('Текст приветствия', blank=True)

    director_name = models.CharField('Имя директора', max_length=200, blank=True)
    director_position = models.CharField('Должность директора', max_length=200, blank=True)
    director_image = models.ImageField('Фото директора', upload_to='homepage/', blank=True)
    director_message = models.TextField('Обращение директора', blank=True)

    slider_title = models.CharField('Заголовок слайдера', max_length=200, default='Добро пожаловать в наш техникум!')
    slider_text = models.TextField('Текст слайдера', default='Мы готовим специалистов с 1944 года')
    slider_image = models.ImageField('Изображение слайдера', upload_to='homepage/', blank=True)

    bento_title = models.CharField('Заголовок быстрых ссылок', max_length=200, default='Быстрые ссылки')

    specialties_label = models.CharField('Подпись блока специальностей', max_length=100, default='Образование', blank=True)
    specialties_title = models.CharField(
        'Заголовок специальностей',
        max_length=300,
        default='Мы обучаем востребованным специальностям',
    )
    specialties_text = models.TextField(
        'Текст специальностей',
        blank=True,
        default='Среднее профессиональное образование по очной форме. Поступление после 9 и 11 классов.',
    )
    specialties_image = models.ImageField('Фото блока специальностей', upload_to='homepage/', blank=True)
    specialties_count = models.CharField('Число специальностей', max_length=10, default='7', blank=True)
    specialties_list = models.TextField(
        'Список специальностей (каждая с новой строки: иконка|название|код)',
        blank=True,
        help_text='Пример: fa-plane|Туризм и гостеприимство|43.02.16',
    )

    hotline_text = models.TextField('Текст телефона доверия', blank=True)
    vov_text = models.CharField('Текст блока ВОВ', max_length=300, blank=True, default='Победа в Великой Отечественной войне 1941-1945')
    vov_image = models.ImageField('Изображение ВОВ', upload_to='homepage/', blank=True)

    contacts_title = models.CharField('Заголовок контактов', max_length=200, default='Контакты')
    contacts_address = models.CharField('Адрес', max_length=300, blank=True)
    contacts_phone = models.CharField('Телефон контактов', max_length=100, blank=True)
    contacts_phone2 = models.CharField('Доп. телефон', max_length=100, blank=True)
    contacts_email = models.EmailField('Email контактов', blank=True)
    contacts_hours = models.CharField('Режим работы', max_length=200, blank=True)
    contacts_map_url = models.URLField('Ссылка на карту (iframe)', blank=True)

    footer_tagline = models.CharField(
        'Текст в подвале',
        max_length=300,
        default='Качество образование — наша главная цель',
        blank=True,
    )
    footer_copyright = models.CharField(
        'Копирайт',
        max_length=300,
        default='© 2026 Техникум. Все права защищены.',
        blank=True,
    )

    updated_at = models.DateTimeField('Обновлено', auto_now=True)

    class Meta:
        verbose_name = 'Главная страница'
        verbose_name_plural = 'Главная страница'

    def __str__(self):
        return 'Настройки главной страницы'

    def save(self, *args, **kwargs):
        self.pk = 1
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        pass

    @classmethod
    def load(cls):
        obj, created = cls.objects.get_or_create(pk=1)
        return obj

    def get_specialties_items(self):
        items = []
        for line in self.specialties_list.splitlines():
            line = line.strip()
            if not line:
                continue
            parts = line.split('|')
            if len(parts) >= 3:
                items.append({'icon': parts[0].strip(), 'title': parts[1].strip(), 'code': parts[2].strip()})
        return items


class ContentTable(models.Model):
    """Переиспользуемая таблица / HTML-блок"""
    title = models.CharField('Название', max_length=200)
    slug = models.SlugField('Код', max_length=200, unique=True, blank=True)
    content = RichTextUploadingField('Содержимое')
    created_at = models.DateTimeField('Создано', auto_now_add=True)
    updated_at = models.DateTimeField('Обновлено', auto_now=True)

    class Meta:
        verbose_name = 'Таблица'
        verbose_name_plural = 'Таблицы'
        ordering = ['title']

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title, allow_unicode=True)
        super().save(*args, **kwargs)


class HomeQuickLink(models.Model):
    """Плитка быстрой ссылки на главной (bento)"""
    STYLE_CHOICES = [
        ('bento-g1', 'Зелёный 1 (большая)'),
        ('bento-g2', 'Зелёный 2'),
        ('bento-g3', 'Зелёный 3'),
        ('bento-g4', 'Зелёный 4'),
        ('bento-g5', 'Зелёный 5'),
        ('bento-g6', 'Зелёный 6'),
        ('bento-g7', 'Зелёный 7'),
        ('bento-g8', 'Зелёный 8'),
        ('bento-contacts', 'Контакты (белая)'),
    ]

    label = models.CharField('Подпись', max_length=100, blank=True)
    title = models.CharField('Заголовок', max_length=200)
    description = models.TextField('Описание', blank=True)
    url = models.CharField('Ссылка', max_length=500, blank=True)
    icon = models.CharField('Иконка FontAwesome', max_length=100, default='fas fa-link')
    style = models.CharField('Стиль', max_length=30, choices=STYLE_CHOICES, default='bento-g2')
    is_large = models.BooleanField('Большая плитка', default=False)
    is_contacts = models.BooleanField('Блок контактов', default=False)
    contacts_list = models.TextField(
        'Список контактов (каждая строка: иконка|текст|ссылка)',
        blank=True,
        help_text='Пример: fa-phone|8-988-480-06-92|tel:+79884800692',
    )
    stat_num = models.CharField('Число статистики', max_length=20, blank=True)
    stat_label = models.CharField('Подпись статистики', max_length=100, blank=True)
    order = models.IntegerField('Порядок', default=0)
    is_active = models.BooleanField('Активна', default=True)
    open_in_new_tab = models.BooleanField('Открывать в новой вкладке', default=False)

    class Meta:
        verbose_name = 'Быстрая ссылка'
        verbose_name_plural = 'Быстрые ссылки главной'
        ordering = ['order', 'title']

    def __str__(self):
        return self.title

    def get_contacts_items(self):
        items = []
        for line in self.contacts_list.splitlines():
            line = line.strip()
            if not line:
                continue
            parts = line.split('|')
            if len(parts) >= 2:
                items.append({
                    'icon': parts[0].strip(),
                    'text': parts[1].strip(),
                    'url': parts[2].strip() if len(parts) > 2 else '',
                })
        return items


class HomeBlock(models.Model):
    """Произвольный блок на главной странице"""
    BLOCK_TYPES = [
        ('text', 'Текст / HTML'),
        ('welcome', 'Приветствие'),
        ('director', 'Обращение директора'),
        ('html', 'Произвольный HTML'),
    ]

    block_type = models.CharField('Тип', max_length=20, choices=BLOCK_TYPES, default='text')
    title = models.CharField('Заголовок', max_length=200, blank=True)
    content = RichTextUploadingField('Содержимое', blank=True)
    order = models.IntegerField('Порядок', default=0)
    is_active = models.BooleanField('Активен', default=True)

    class Meta:
        verbose_name = 'Блок главной'
        verbose_name_plural = 'Блоки главной'
        ordering = ['order']

    def __str__(self):
        return self.title or f'Блок {self.get_block_type_display()}'


class News(models.Model):
    """Новость"""
    title = models.CharField('Заголовок', max_length=200)
    slug = models.SlugField('URL', max_length=200, unique=True, blank=True)
    excerpt = models.TextField('Краткое описание', blank=True)
    content = RichTextUploadingField('Содержимое', blank=True)
    image = models.ImageField('Изображение', upload_to='news/', blank=True)
    tag = models.CharField('Тег', max_length=50, blank=True, default='Новость')
    is_published = models.BooleanField('Опубликовано', default=True)
    created_at = models.DateTimeField('Дата публикации', auto_now_add=True)
    updated_at = models.DateTimeField('Обновлено', auto_now=True)

    class Meta:
        verbose_name = 'Новость'
        verbose_name_plural = 'Новости'
        ordering = ['-created_at']

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            from django.utils.text import slugify
            self.slug = slugify(self.title, allow_unicode=True)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return f'/news/{self.slug}/'


class Banner(models.Model):
    """Рекламный баннер на главной странице"""
    title = models.CharField('Название', max_length=200)
    image = models.ImageField('Изображение', upload_to='banners/')
    url = models.URLField('Ссылка', blank=True)
    order = models.IntegerField('Порядок', default=0)
    is_active = models.BooleanField('Активен', default=True)

    class Meta:
        verbose_name = 'Баннер'
        verbose_name_plural = 'Баннеры'
        ordering = ['order']

    def __str__(self):
        return self.title


class Gallery(models.Model):
    """Галерея изображений"""
    page = models.ForeignKey(
        Page,
        on_delete=models.CASCADE,
        related_name='galleries',
        verbose_name='Страница',
        null=True,
        blank=True
    )
    title = models.CharField('Название', max_length=200)
    description = models.TextField('Описание', blank=True)
    is_active = models.BooleanField('Активна', default=True)
    
    created_at = models.DateTimeField('Создано', auto_now_add=True)
    updated_at = models.DateTimeField('Обновлено', auto_now=True)

    class Meta:
        verbose_name = 'Галерея'
        verbose_name_plural = 'Галереи'
        ordering = ['-created_at']

    def __str__(self):
        return self.title


class GalleryImage(models.Model):
    """Изображение в галерее"""
    gallery = models.ForeignKey(
        Gallery,
        on_delete=models.CASCADE,
        related_name='images',
        verbose_name='Галерея'
    )
    image = models.ImageField('Изображение', upload_to='gallery/%Y/%m/')
    title = models.CharField('Название', max_length=200, blank=True)
    description = models.TextField('Описание', blank=True)
    order = models.IntegerField('Порядок', default=0)
    
    created_at = models.DateTimeField('Создано', auto_now_add=True)

    class Meta:
        verbose_name = 'Изображение'
        verbose_name_plural = 'Изображения'
        ordering = ['order', 'created_at']

    def __str__(self):
        return self.title or f'Изображение {self.id}'



class EducationalProgram(models.Model):
    """Образовательная программа (специальность)"""
    page = models.ForeignKey(
        Page,
        on_delete=models.CASCADE,
        related_name='edu_programs',
        verbose_name='Страница',
        null=True, blank=True
    )
    code = models.CharField('Код специальности', max_length=20, blank=True)
    title = models.CharField('Название специальности', max_length=300)
    qualification = models.CharField('Квалификация', max_length=200, blank=True)
    duration = models.CharField('Срок обучения', max_length=100, blank=True)
    form = models.CharField('Форма обучения', max_length=100, blank=True, default='Очная')
    icon = models.CharField(
        'Иконка FontAwesome',
        max_length=100,
        default='fas fa-graduation-cap',
        blank=True,
        help_text='Например: fas fa-calculator',
    )
    description = models.TextField('Описание (для карточки)', blank=True)
    image = models.ImageField('Изображение', upload_to='programs/', blank=True)
    show_on_homepage = models.BooleanField('Показывать на главной', default=True)
    order = models.IntegerField('Порядок', default=0)
    is_active = models.BooleanField('Активна', default=True)

    class Meta:
        verbose_name = 'Образовательная программа'
        verbose_name_plural = 'Образовательные программы'
        ordering = ['order', 'code']

    def __str__(self):
        return f'{self.code} {self.title}' if self.code else self.title

    @property
    def display_title(self):
        return f'{self.code} {self.title}'.strip() if self.code else self.title

    def get_image_url(self):
        if self.image and self.image.name:
            return self.image.url
        return ''


class AdmissionYear(models.Model):
    """Год поступления для образовательной программы"""
    program = models.ForeignKey(
        EducationalProgram,
        on_delete=models.CASCADE,
        related_name='years',
        verbose_name='Программа'
    )
    year = models.IntegerField('Год поступления')
    order = models.IntegerField('Порядок', default=0)
    is_active = models.BooleanField('Активен', default=True)

    class Meta:
        verbose_name = 'Год поступления'
        verbose_name_plural = 'Годы поступления'
        ordering = ['-year']
        unique_together = [('program', 'year')]

    def __str__(self):
        return f'{self.program} — {self.year}'


class ProgramDocument(models.Model):
    """Документ образовательной программы"""
    DOC_TYPES = [
        ('opop', 'ОПОП (основная программа)'),
        ('rup', 'Рабочий учебный план'),
        ('calendar', 'Календарный учебный график'),
        ('annotation', 'Аннотации рабочих программ'),
        ('fos', 'Фонд оценочных средств'),
        ('practice', 'Программа практики'),
        ('other', 'Прочее'),
    ]

    year = models.ForeignKey(
        AdmissionYear,
        on_delete=models.CASCADE,
        related_name='documents',
        verbose_name='Год поступления'
    )
    doc_type = models.CharField('Тип документа', max_length=50, choices=DOC_TYPES, default='opop')
    title = models.CharField('Название документа', max_length=300)
    file = models.FileField('Файл', upload_to='edu_programs/%Y/', blank=True, null=True)
    order = models.IntegerField('Порядок', default=0)
    is_active = models.BooleanField('Активен', default=True)

    class Meta:
        verbose_name = 'Документ программы'
        verbose_name_plural = 'Документы программы'
        ordering = ['order', 'doc_type']

    def __str__(self):
        return self.title
