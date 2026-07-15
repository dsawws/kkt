from django.core.management.base import BaseCommand
from cms.models import (
    MenuItem, Page, HomePage, HomeQuickLink, HomeBlock,
    EducationalProgram, AdmissionYear,
)


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
        homepage.bento_title = 'Быстрые ссылки'
        homepage.specialties_list = '\n'.join([
            'fa-plane|Туризм и гостеприимство|43.02.16',
            'fa-truck|Операционная деятельность в логистике|38.02.03',
            'fa-store|Торговое дело|38.02.08',
            'fa-calculator|Экономика и бухгалтерский учёт|38.02.01',
            'fa-balance-scale|Юриспруденция|40.02.04',
            'fa-code|Разработка и управление ПО|09.02.11',
            'fa-map-marked-alt|Землеустройство|21.02.19',
        ])
        homepage.contacts_address = 'Краснодарский край, 352630, г. Белореченск, ул. Кирова, д. 4'
        homepage.contacts_phone = '8(86155)2-27-83'
        homepage.contacts_phone2 = '8-988-480-06-92 (приёмная комиссия)'
        homepage.contacts_email = 'kktbel@mail.ru'
        homepage.contacts_hours = 'Ежедневно с 8:00 - 17:00'
        homepage.contacts_map_url = (
            'https://yandex.ru/map-widget/v1/?ll=39.881309%2C44.752871&mode=search&ol=geo'
            '&ouri=ymapsbm1%3A%2F%2Fgeo%3Fdata%3DCgoxNTAyODkzNjE3EmXQoNC-0YHRgdC40Y8sINCa0YDQsNGB0L3QvtC00LDRgNGB0LrQuNC5INC60YDQsNC5LCDQkdC10LvQvtGA0LXRh9C10L3RgdC6LCDRg9C70LjRhtCwINCa0LjRgNC-0LLQsCwgNCIKDXWGH0IV8QIzQg%2C%2C&z=17.13'
        )
        homepage.hotline_text = (
            'Единый телефон доверия для детей и подростков 8-800-2000-122\n'
            'Звонок бесплатный и круглосуточный.'
        )
        homepage.save()
        self.stdout.write(self.style.SUCCESS('[OK] Главная страница обновлена'))

        if not HomeQuickLink.objects.exists():
            quick_links = [
                {'label': 'Раздел', 'title': 'Поступающим', 'description': 'Условия приёма, документы, приказы о зачислении', 'url': '/page/abiturient/', 'icon': 'fas fa-user-graduate', 'style': 'bento-g1', 'is_large': True, 'stat_num': '2026', 'stat_label': 'учебный год', 'order': 1},
                {'label': 'Платформа', 'title': 'Moodle', 'description': 'Дистанционное обучение', 'url': 'http://e-learn.kktbel.ru/login/index.php', 'icon': 'fas fa-laptop', 'style': 'bento-g2', 'open_in_new_tab': True, 'order': 2},
                {'label': 'Мобильное', 'title': 'Приложение', 'description': 'Расписание, оценки, объявления', 'url': '#', 'icon': 'fas fa-mobile-alt', 'style': 'bento-g3', 'order': 3},
                {'label': 'Оплата', 'title': 'Оплата обучения', 'description': 'Онлайн-оплата и реквизиты', 'url': '/page/platnye-uslugi/', 'icon': 'fas fa-credit-card', 'style': 'bento-g4', 'order': 4},
                {'label': 'Связь', 'title': 'Написать нам', 'description': 'Онлайн-консультация ВКонтакте', 'url': 'https://vk.com/im?sel=-belkkt', 'icon': 'fab fa-vk', 'style': 'bento-g5', 'open_in_new_tab': True, 'order': 5},
                {'label': 'Студентам', 'title': 'Общежитие', 'description': 'Условия проживания', 'url': '/page/student/', 'icon': 'fas fa-building', 'style': 'bento-g6', 'order': 6},
                {'label': 'Контакты', 'title': 'Как нас найти', 'description': '', 'url': '', 'icon': 'fas fa-map-marker-alt', 'style': 'bento-contacts', 'is_contacts': True, 'order': 7,
                 'contacts_list': 'fa-map-marker-alt|352630, Краснодарский край, г. Белореченск, ул. Кирова, д. 4|\nfa-phone|8 (86155) 2-27-83|tel:+78615522783\nfa-phone|8-988-480-06-92|tel:+79884800692\nfa-envelope|kktbel@mail.ru|mailto:kktbel@mail.ru'},
            ]
            for ql in quick_links:
                HomeQuickLink.objects.create(**ql)
            self.stdout.write(self.style.SUCCESS('[OK] Быстрые ссылки созданы'))

        if not HomeBlock.objects.exists():
            HomeBlock.objects.create(
                block_type='welcome', title='Уважаемые посетители!',
                content=homepage.welcome_text.replace('\n', '<br>'),
                order=1,
            )
            self.stdout.write(self.style.SUCCESS('[OK] Блоки главной созданы'))

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
            self.stdout.write(self.style.SUCCESS(f'[OK] {pd["title"]}'))

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
            self.stdout.write(self.style.SUCCESS(f'  [->] {sp["title"]}'))

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

        self._seed_educational_programs(created_pages.get('professions'))

        self.stdout.write(self.style.SUCCESS('\n[OK] Готово! Запустите сервер: py manage.py runserver 0.0.0.0:8000'))

    def _seed_educational_programs(self, professions_page):
        if EducationalProgram.objects.exists():
            self.stdout.write('  — программы уже есть, пропуск')
            return

        programs = [
            {
                'code': '43.02.16', 'title': 'Туризм и гостеприимство',
                'icon': 'fas fa-plane', 'duration': '2 года 10 месяцев',
                'qualification': 'специалист по туризму и гостеприимству',
                'description': 'Подготовка специалистов для гостиничного и туристического бизнеса.',
                'order': 1,
            },
            {
                'code': '38.02.03', 'title': 'Операционная деятельность в логистике',
                'icon': 'fas fa-truck', 'duration': '2 года 10 месяцев',
                'qualification': 'операционный логист',
                'description': 'Организация перевозок, складирования и управления цепями поставок.',
                'order': 2,
            },
            {
                'code': '38.02.08', 'title': 'Торговое дело',
                'icon': 'fas fa-store', 'duration': '2 года 10 месяцев',
                'qualification': 'специалист торгового дела',
                'description': 'Коммерческая деятельность, маркетинг и товароведение.',
                'order': 3,
            },
            {
                'code': '38.02.01', 'title': 'Экономика и бухгалтерский учёт',
                'icon': 'fas fa-calculator', 'duration': '2 года 10 месяцев',
                'qualification': 'бухгалтер',
                'description': 'Бухгалтерский учёт, налогообложение и финансовый анализ.',
                'order': 4,
            },
            {
                'code': '40.02.04', 'title': 'Юриспруденция',
                'icon': 'fas fa-balance-scale', 'duration': '2 года 10 месяцев',
                'qualification': 'юрист',
                'description': 'Правовое сопровождение и работа с документами правового характера.',
                'order': 5,
            },
            {
                'code': '09.02.11', 'title': 'Разработка и управление ПО',
                'icon': 'fas fa-code', 'duration': '3 года 10 месяцев',
                'qualification': 'разработчик программного обеспечения',
                'description': 'Разработка, тестирование и сопровождение программных продуктов.',
                'order': 6,
            },
            {
                'code': '21.02.19', 'title': 'Землеустройство',
                'icon': 'fas fa-map-marked-alt', 'duration': '3 года 10 месяцев',
                'qualification': 'специалист по землеустройству',
                'description': 'Кадастровый учёт, геодезия и земельно-имущественные отношения.',
                'order': 7,
            },
        ]

        for data in programs:
            prog = EducationalProgram.objects.create(
                page=professions_page,
                show_on_homepage=True,
                is_active=True,
                form='Очная',
                **data,
            )
            AdmissionYear.objects.get_or_create(
                program=prog, year=2025,
                defaults={'is_active': True, 'order': 1},
            )
            self.stdout.write(self.style.SUCCESS(f'  [OK] Программа: {prog.code} {prog.title}'))

        if professions_page:
            professions_page.content = ''
            professions_page.description = (
                'Выберите интересующую вас специальность, чтобы узнать подробности обучения'
            )
            professions_page.save(update_fields=['content', 'description'])
            self.stdout.write(self.style.SUCCESS('  [OK] Страница «Специальности» переведена на программы из админки'))
