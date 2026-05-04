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
        if self.page:
            return f'/page/{self.page.slug}/'
        return f'/page/{self.slug}/'


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
        # ССК
        ('ssk_docs', 'Документы ССК'),
        # Антинарко
        ('antinarko_docs', 'Антинарко'),
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
    file = models.FileField('Файл', upload_to='documents/%Y/%m/')
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
    welcome_title = models.CharField('Заголовок приветствия', max_length=200, default='Добро пожаловать!')
    welcome_text = models.TextField('Текст приветствия', blank=True)
    
    director_name = models.CharField('Имя директора', max_length=200, blank=True)
    director_position = models.CharField('Должность директора', max_length=200, blank=True)
    director_image = models.ImageField('Фото директора', upload_to='homepage/', blank=True)
    director_message = models.TextField('Обращение директора', blank=True)
    
    slider_title = models.CharField('Заголовок слайдера', max_length=200, default='Добро пожаловать в наш техникум!')
    slider_text = models.TextField('Текст слайдера', default='Мы готовим специалистов с 1944 года')
    slider_image = models.ImageField('Изображение слайдера', upload_to='homepage/', blank=True)
    
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
    order = models.IntegerField('Порядок', default=0)
    is_active = models.BooleanField('Активна', default=True)

    class Meta:
        verbose_name = 'Образовательная программа'
        verbose_name_plural = 'Образовательные программы'
        ordering = ['order', 'code']

    def __str__(self):
        return f'{self.code} {self.title}' if self.code else self.title


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
