from django.test import TestCase
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
