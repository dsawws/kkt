from django.core.management.base import BaseCommand
from cms.models import MenuItem, Page, HomePage


class Command(BaseCommand):
    help = 'Создает начальные данные для сайта'

    def handle(self, *args, **options):
        self.stdout.write('Создание начальных данных...')

        # Главная страница
        homepage, _ = HomePage.objects.get_or_create(pk=1)
        homepage.welcome_title = 'Уважаемые посетители!'
        homepage.welcome_text = (
            'Мы рады приветствовать Вас на сайте Краснодарского кооперативного техникума!\n\n'
            'Мы готовим специалистов уже с 1944 года, и все эти годы неизменным для нас остается только одно — '
            'это высокое качество образования. Наш техникум является сильным, проверенным временем, учебным заведением! '
            'Здесь студенты получают знания, которые позволяют им успешно трудоустроиться, дают возможность занять достойное место в жизни!\n\n'
            'Наша важнейшая задача — организовать образовательный процесс так, чтобы каждый студент овладел выбранной профессией '
            'на высоком уровне и получил не только теоретические знания, но и хороший практический опыт. '
            'Наши образовательные программы учитывают запросы работодателей. '
            'Студенты техникума проходят практическую подготовку на крупных предприятиях района и края!\n\n'
            'Мы поддерживаем связь с нашими выпускниками, помогаем им в трудоустройстве. '
            'Добро пожаловать в нашу большую и дружную семью!'
        )
        homepage.director_name = 'Нанаев В.В.'
        homepage.director_position = 'Директор техникума'
        homepage.slider_title = 'Добро пожаловать в наш техникум!'
        homepage.slider_text = 'Мы готовим специалистов с 1944 года'
        homepage.save()
        self.stdout.write(self.style.SUCCESS('✓ Главная страница обновлена'))

        # Основные страницы навбара
        top_pages = [
            {'title': 'Сведения об организации', 'slug': 'basic-info', 'order': 1},
            {'title': 'Поступающим',              'slug': 'abiturient',   'order': 2},
            {'title': 'Студентам',                'slug': 'student',      'order': 3},
            {'title': 'Преподавателям',           'slug': 'teacher',      'order': 4},
            {'title': 'Специальности',            'slug': 'professions',  'order': 5},
            {'title': 'Новости',                  'slug': 'news',         'order': 6},
            {'title': 'Обркредит в СПО',          'slug': 'kredit',       'order': 7},
            {'title': 'ССК',                      'slug': 'ssk',          'order': 8},
            {'title': 'Антинарко',                'slug': 'antinarko',    'order': 9},
            {'title': 'Профилактика',             'slug': 'profilaktika', 'order': 10},
        ]

        created_pages = {}
        for pd in top_pages:
            page, _ = Page.objects.get_or_create(
                slug=pd['slug'],
                defaults={'title': pd['title'], 'is_published': True}
            )
            created_pages[pd['slug']] = page

            mi, _ = MenuItem.objects.get_or_create(
                slug=pd['slug'],
                defaults={'title': pd['title'], 'page': page, 'is_active': True, 'order': pd['order']}
            )
            self.stdout.write(self.style.SUCCESS(f'✓ {pd["title"]}'))

        # Подстраницы "Сведения об организации"
        basic_info_page = created_pages['basic-info']
        basic_info_menu = MenuItem.objects.get(slug='basic-info')

        sub_pages = [
            {'title': 'Основные сведения',                                          'slug': 'osnovnye-svedeniya',       'order': 1},
            {'title': 'Структура и органы управления',                              'slug': 'struktura',                'order': 2},
            {'title': 'Документы',                                                  'slug': 'dokumenty',                'order': 3},
            {'title': 'Образование',                                                'slug': 'obrazovanie',              'order': 4},
            {'title': 'Образовательные стандарты',                                  'slug': 'obrazovatelnye-standarty', 'order': 5},
            {'title': 'Руководство. Педагогический (научно-педагогический) состав', 'slug': 'rukovodstvo',              'order': 6},
            {'title': 'Педагогический состав',                                      'slug': 'pedagogicheskiy-sostav',   'order': 7},
            {'title': 'Материально-техническое обеспечение',                        'slug': 'materialno-tekhnicheskoe', 'order': 8},
            {'title': 'Платные образовательные услуги',                             'slug': 'platnye-uslugi',           'order': 9},
            {'title': 'Финансово-хозяйственная деятельность',                       'slug': 'finansy',                  'order': 10},
            {'title': 'Вакантные места для приёма',                                 'slug': 'vakantnye-mesta',          'order': 11},
            {'title': 'Стипендии и меры поддержки',                                 'slug': 'stipendii',                'order': 12},
            {'title': 'Международное сотрудничество',                               'slug': 'mezhdunarodnoe',           'order': 13},
            {'title': 'Организация питания',                                        'slug': 'pitanie',                  'order': 14},
        ]

        for sp in sub_pages:
            page, _ = Page.objects.get_or_create(
                slug=sp['slug'],
                defaults={'title': sp['title'], 'is_published': True}
            )
            mi, _ = MenuItem.objects.get_or_create(
                slug=sp['slug'],
                defaults={
                    'title': sp['title'],
                    'page': page,
                    'parent': basic_info_menu,
                    'is_active': True,
                    'order': sp['order'],
                }
            )
            self.stdout.write(self.style.SUCCESS(f'  ↳ {sp["title"]}'))

        # Контент страницы "Основные сведения"
        osnovnye, _ = Page.objects.get_or_create(slug='osnovnye-svedeniya', defaults={'title': 'Основные сведения'})
        if not osnovnye.content:
            osnovnye.content = """
<table class="content-table" style="width:100%; border-collapse:collapse;">
  <tbody>
    <tr><td style="padding:8px; border:1px solid #ddd; font-weight:bold; width:40%;">Полное наименование</td>
        <td style="padding:8px; border:1px solid #ddd;">Автономная некоммерческая частная профессиональная образовательная организация «Краснодарский кооперативный техникум крайпотребсоюза»</td></tr>
    <tr><td style="padding:8px; border:1px solid #ddd; font-weight:bold;">Сокращённое наименование</td>
        <td style="padding:8px; border:1px solid #ddd;">АНЧ ПОО «Краснодарский кооперативный техникум крайпотребсоюза»</td></tr>
    <tr><td style="padding:8px; border:1px solid #ddd; font-weight:bold;">Учредитель</td>
        <td style="padding:8px; border:1px solid #ddd;">Краснодарский краевой союз потребительских обществ (Краснодарский крайпотребсоюз)</td></tr>
    <tr><td style="padding:8px; border:1px solid #ddd; font-weight:bold;">Руководитель учредителя (РУК)</td>
        <td style="padding:8px; border:1px solid #ddd;">Автономная некоммерческая образовательная организация высшего образования Центросоюза Российской Федерации «Российский университет кооперации» (Российский университет кооперации)</td></tr>
    <tr><td style="padding:8px; border:1px solid #ddd; font-weight:bold;">Дата создания</td>
        <td style="padding:8px; border:1px solid #ddd;">1944 год</td></tr>
    <tr><td style="padding:8px; border:1px solid #ddd; font-weight:bold;">Место нахождения</td>
        <td style="padding:8px; border:1px solid #ddd;">352630, Краснодарский край, г. Белореченск, ул. Кирова, д. 4</td></tr>
    <tr><td style="padding:8px; border:1px solid #ddd; font-weight:bold;">Места осуществления образовательной деятельности</td>
        <td style="padding:8px; border:1px solid #ddd;">352630, Краснодарский край, г. Белореченск, ул. Кирова, д. 4</td></tr>
    <tr><td style="padding:8px; border:1px solid #ddd; font-weight:bold;">Телефон</td>
        <td style="padding:8px; border:1px solid #ddd;">8(86155) 2-27-83</td></tr>
    <tr><td style="padding:8px; border:1px solid #ddd; font-weight:bold;">Электронная почта</td>
        <td style="padding:8px; border:1px solid #ddd;">kktbel@mail.ru</td></tr>
    <tr><td style="padding:8px; border:1px solid #ddd; font-weight:bold;">Сайт</td>
        <td style="padding:8px; border:1px solid #ddd;"><a href="http://kktbel.ru">kktbel.ru</a></td></tr>
    <tr><td style="padding:8px; border:1px solid #ddd; font-weight:bold;">Режим работы</td>
        <td style="padding:8px; border:1px solid #ddd;">Ежедневно с 8:00 до 17:00</td></tr>
  </tbody>
</table>
"""
            osnovnye.save()

        # Контент "Международное сотрудничество"
        mezh, _ = Page.objects.get_or_create(slug='mezhdunarodnoe', defaults={'title': 'Международное сотрудничество'})
        if not mezh.content:
            mezh.content = """
<h2>О заключённых и планируемых к заключению договорах с иностранными и (или) международными организациями по вопросам образования и науки</h2>
<p>У образовательной организации нет заключённых и планируемых к заключению договоров с иностранными и (или) международными организациями по вопросам образования и науки.</p>
"""
            mezh.save()

        # Контент "Организация питания"
        pitanie, _ = Page.objects.get_or_create(slug='pitanie', defaults={'title': 'Организация питания'})
        if not pitanie.content:
            pitanie.content = """
<h2>Организация питания в образовательной организации</h2>
<p>По вопросам организации питания:</p>
<p><strong>Ответственный за организацию питания:</strong><br>
Индивидуальный предприниматель Трофимов М.В.</p>
"""
            pitanie.save()

        # Контент "Платные образовательные услуги"
        platnye, _ = Page.objects.get_or_create(slug='platnye-uslugi', defaults={'title': 'Платные образовательные услуги'})
        if not platnye.content:
            platnye.content = """
<h2>Памятка</h2>
<p><strong>Важная информация:</strong></p>
<ul>
  <li>Оплата производится за каждый семестр обучения или за год</li>
  <li>При наличии льгот (инвалиды, дети-сироты, опекаемые) необходимо предоставить подтверждающие документы</li>
  <li>Все вопросы по оплате можно уточнить в бухгалтерии АНЧ ПОО «Краснодарский кооперативный техникум крайпотребсоюза» (этаж 1. Бухгалтерия)</li>
</ul>
"""
            platnye.save()

        self.stdout.write(self.style.SUCCESS('\n✓ Готово! Запустите сервер: py manage.py runserver 0.0.0.0:8000'))
