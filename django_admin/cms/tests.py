from django.contrib.auth.models import User
from django.test import Client, TestCase
from django.urls import reverse

from .models import MenuItem, Page, HomePage, Document


class MenuItemTestCase(TestCase):
    def setUp(self):
        self.page = Page.objects.create(
            title='Test Page',
            slug='test-page',
            is_published=True
        )
        
    def test_menu_item_creation(self):
        menu_item = MenuItem.objects.create(
            title='Test Menu',
            page=self.page
        )
        self.assertEqual(menu_item.title, 'Test Menu')
        self.assertEqual(menu_item.slug, 'test-menu')
        
    def test_menu_hierarchy(self):
        parent = MenuItem.objects.create(title='Parent')
        child = MenuItem.objects.create(title='Child', parent=parent)
        self.assertEqual(child.parent, parent)
        self.assertIn(child, parent.get_children())


class MenuItemPanelSaveTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='staff',
            password='pass',
            is_staff=True,
        )
        self.client.force_login(self.user)
        self.item = MenuItem.objects.create(
            title='Обркредит в СПО',
            slug='kredit',
            order=3,
            is_active=True,
        )

    def _post_payload(self, **extra):
        data = {
            'title': self.item.title,
            'slug': self.item.slug,
            'parent': '',
            'page': '',
            'order': self.item.order,
            'is_active': 'on',
        }
        data.update(extra)
        return data

    def test_edit_form_has_continue_button(self):
        response = self.client.get(reverse('panel:menu_edit', args=[self.item.pk]))
        self.assertEqual(response.status_code, 200)
        content = response.content.decode()
        self.assertIn('name="_save"', content)
        self.assertIn('name="_continue"', content)
        self.assertIn('Сохранить и продолжить редактирование', content)

    def test_save_redirects_to_list(self):
        response = self.client.post(
            reverse('panel:menu_edit', args=[self.item.pk]),
            self._post_payload(_save='1'),
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('panel:menu_list'))

    def test_save_and_continue_stays_on_edit(self):
        response = self.client.post(
            reverse('panel:menu_edit', args=[self.item.pk]),
            self._post_payload(_continue='1', title='Обркредит обновлён'),
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('panel:menu_edit', args=[self.item.pk]))
        self.item.refresh_from_db()
        self.assertEqual(self.item.title, 'Обркредит обновлён')

    def test_add_and_continue_opens_new_item_edit(self):
        response = self.client.post(
            reverse('panel:menu_add'),
            {
                'title': 'Новый пункт',
                'slug': 'new-item',
                'parent': '',
                'page': '',
                'order': 10,
                'is_active': 'on',
                '_continue': '1',
            },
        )
        self.assertEqual(response.status_code, 302)
        created = MenuItem.objects.get(slug='new-item')
        self.assertEqual(response.url, reverse('panel:menu_edit', args=[created.pk]))


class PageTestCase(TestCase):
    def test_page_creation(self):
        page = Page.objects.create(
            title='Test Page',
            description='Test description',
            is_published=True
        )
        self.assertEqual(page.slug, 'test-page')
        self.assertTrue(page.is_published)
        
    def test_page_url(self):
        page = Page.objects.create(title='Test', slug='test')
        self.assertEqual(page.get_absolute_url(), '/page/test/')


class HomePageTestCase(TestCase):
    def test_homepage_singleton(self):
        homepage1 = HomePage.load()
        homepage2 = HomePage.load()
        self.assertEqual(homepage1.pk, homepage2.pk)
        self.assertEqual(HomePage.objects.count(), 1)


class DocumentTestCase(TestCase):
    def setUp(self):
        self.page = Page.objects.create(title='Test', slug='test')
        
    def test_document_creation(self):
        doc = Document.objects.create(
            page=self.page,
            title='Test Document',
            category='dokumenti'
        )
        self.assertEqual(doc.title, 'Test Document')
        self.assertEqual(doc.page, self.page)
