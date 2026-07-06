import os
from datetime import datetime

from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.views.decorators.http import require_POST

from .models import (
    Page, News, Document, DocumentSection, MenuItem, HomePage, HomeQuickLink,
    HomeBlock, Banner, Gallery, GalleryImage, ContentBlock, ContentTable,
    EducationalProgram, AdmissionYear, ProgramDocument,
)
from .panel_utils import sync_page_to_menu, next_quicklink_order, free_quicklink_style
from .panel_forms import (
    PageForm, NewsForm, DocumentForm, DocumentSectionForm, MenuItemForm,
    HomePageForm, HomeQuickLinkForm, HomeBlockForm, BannerForm, GalleryForm,
    ContentBlockForm, ContentTableForm, FooterForm, PanelUserForm,
    EducationalProgramForm, AdmissionYearForm, ProgramDocumentForm,
    GalleryImageFormSet, AdmissionYearFormSet, ProgramDocumentFormSet,
    ContentBlockFormSet,
)


def staff_required(view_func):
    decorated = login_required(
        user_passes_test(lambda u: u.is_staff)(view_func)
    )
    return decorated


def panel_login(request):
    if request.user.is_authenticated and request.user.is_staff:
        return redirect('panel:dashboard')

    error = None
    if request.method == 'POST':
        username = request.POST.get('username', '')
        password = request.POST.get('password', '')
        user = authenticate(request, username=username, password=password)
        if user and user.is_staff:
            login(request, user)
            next_url = request.GET.get('next', reverse('panel:dashboard'))
            return redirect(next_url)
        error = 'Неверный логин или пароль'

    return render(request, 'panel/login.html', {'error': error})


@staff_required
def panel_logout(request):
    logout(request)
    return redirect('panel:login')


@staff_required
def dashboard(request):
    stats = {
        'pages': Page.objects.count(),
        'news': News.objects.count(),
        'documents': Document.objects.count(),
        'menu_items': MenuItem.objects.count(),
        'banners': Banner.objects.count(),
        'galleries': Gallery.objects.count(),
        'programs': EducationalProgram.objects.count(),
    }
    recent_news = News.objects.order_by('-created_at')[:5]
    recent_pages = Page.objects.order_by('-updated_at')[:5]
    return render(request, 'panel/dashboard.html', {
        'stats': stats,
        'recent_news': recent_news,
        'recent_pages': recent_pages,
        'active_menu': 'dashboard',
    })


def _handle_formset(formset, request):
    if formset.is_valid():
        formset.save()
        return True
    return False


# ── Страницы ──────────────────────────────────────────────────────────

@staff_required
def page_list(request):
    pages = Page.objects.select_related('parent').order_by('-updated_at')
    q = request.GET.get('q', '').strip()
    if q:
        from .search_utils import search_pages
        pages = search_pages(Page.objects.all(), q)
    return render(request, 'panel/page_list.html', {
        'objects': pages,
        'q': q,
        'active_menu': 'pages',
        'title': 'Страницы',
        'add_url': reverse('panel:page_add'),
    })


@staff_required
def page_edit(request, pk=None):
    page = get_object_or_404(Page, pk=pk) if pk else None
    block_formset = None

    if request.method == 'POST':
        form = PageForm(request.POST, instance=page)
        block_formset = ContentBlockFormSet(request.POST, instance=page) if page else None
        blocks_ok = block_formset.is_valid() if block_formset else True
        if form.is_valid() and blocks_ok:
            page = form.save()
            if block_formset:
                block_formset.instance = page
                block_formset.save()
            else:
                block_formset = ContentBlockFormSet(instance=page)
            sync_page_to_menu(page)
            messages.success(request, 'Страница сохранена')
            return redirect('panel:page_edit', pk=page.pk)
        elif block_formset and not blocks_ok:
            messages.error(request, 'Проверьте блоки контента')
    else:
        form = PageForm(instance=page)
        if page:
            block_formset = ContentBlockFormSet(instance=page)

    tables = ContentTable.objects.order_by('title')
    documents = Document.objects.filter(is_active=True).select_related('page').order_by('title')[:200]

    return render(request, 'panel/page_form.html', {
        'form': form,
        'object': page,
        'block_formset': block_formset,
        'tables': tables,
        'documents': documents,
        'active_menu': 'pages',
        'title': 'Редактировать страницу' if page else 'Добавить страницу',
    })


@staff_required
@require_POST
def page_delete(request, pk):
    page = get_object_or_404(Page, pk=pk)
    page.delete()
    messages.success(request, f'Страница «{page.title}» удалена')
    return redirect('panel:page_list')


# ── Новости ───────────────────────────────────────────────────────────

@staff_required
def news_list(request):
    items = News.objects.order_by('-created_at')
    q = request.GET.get('q', '').strip()
    if q:
        items = items.filter(Q(title__icontains=q) | Q(content__icontains=q))
    return render(request, 'panel/object_list.html', {
        'objects': items,
        'q': q,
        'active_menu': 'news',
        'title': 'Новости',
        'add_url': reverse('panel:news_add'),
        'edit_url_name': 'panel:news_edit',
        'delete_url_name': 'panel:news_delete',
        'columns': ['title', 'tag', 'is_published', 'created_at'],
    })


@staff_required
def news_edit(request, pk=None):
    obj = get_object_or_404(News, pk=pk) if pk else None
    if request.method == 'POST':
        form = NewsForm(request.POST, request.FILES, instance=obj)
        if form.is_valid():
            form.save()
            messages.success(request, 'Новость сохранена')
            return redirect('panel:news_list')
    else:
        form = NewsForm(instance=obj)
    return render(request, 'panel/object_form.html', {
        'form': form,
        'object': obj,
        'active_menu': 'news',
        'title': 'Редактировать новость' if obj else 'Добавить новость',
        'back_url': reverse('panel:news_list'),
        'preview_url': obj.get_absolute_url() if obj else None,
    })


@staff_required
@require_POST
def news_delete(request, pk):
    obj = get_object_or_404(News, pk=pk)
    obj.delete()
    messages.success(request, 'Новость удалена')
    return redirect('panel:news_list')


# ── Документы ─────────────────────────────────────────────────────────

@staff_required
def document_list(request):
    items = Document.objects.select_related('page').order_by('page', 'category', 'order')
    q = request.GET.get('q', '').strip()
    page_filter = request.GET.get('page', '')
    if q:
        items = items.filter(Q(title__icontains=q) | Q(description__icontains=q))
    if page_filter:
        items = items.filter(page_id=page_filter)
    pages = Page.objects.order_by('title')
    return render(request, 'panel/document_list.html', {
        'objects': items,
        'q': q,
        'page_filter': page_filter,
        'pages': pages,
        'active_menu': 'documents',
        'title': 'Документы',
        'add_url': reverse('panel:document_add'),
    })


@staff_required
def document_edit(request, pk=None):
    obj = get_object_or_404(Document, pk=pk) if pk else None
    page_id = request.GET.get('page') or request.POST.get('page') or request.POST.get('return_page')
    if request.method == 'POST':
        form = DocumentForm(request.POST, request.FILES, instance=obj)
        if form.is_valid():
            doc = form.save()
            messages.success(request, 'Документ сохранён')
            if page_id:
                return redirect('panel:page_edit', pk=page_id)
            return redirect('panel:document_list')
    else:
        form = DocumentForm(instance=obj)
        if not obj and page_id:
            form.initial['page'] = page_id
    back_url = reverse('panel:page_edit', kwargs={'pk': page_id}) if page_id else reverse('panel:document_list')
    return render(request, 'panel/object_form.html', {
        'form': form,
        'object': obj,
        'active_menu': 'documents',
        'title': 'Редактировать документ' if obj else 'Добавить документ',
        'back_url': back_url,
    })


@staff_required
@require_POST
def document_delete(request, pk):
    obj = get_object_or_404(Document, pk=pk)
    obj.delete()
    messages.success(request, 'Документ удалён')
    return redirect('panel:document_list')


# ── Разделы документов ────────────────────────────────────────────────

@staff_required
def docsection_list(request):
    items = DocumentSection.objects.select_related('page').order_by('page', 'order')
    return render(request, 'panel/object_list.html', {
        'objects': items,
        'active_menu': 'docsections',
        'title': 'Разделы документов',
        'add_url': reverse('panel:docsection_add'),
        'edit_url_name': 'panel:docsection_edit',
        'delete_url_name': 'panel:docsection_delete',
        'columns': ['page', 'title', 'category', 'order', 'is_active'],
    })


@staff_required
def docsection_edit(request, pk=None):
    obj = get_object_or_404(DocumentSection, pk=pk) if pk else None
    if request.method == 'POST':
        form = DocumentSectionForm(request.POST, instance=obj)
        if form.is_valid():
            form.save()
            messages.success(request, 'Раздел сохранён')
            return redirect('panel:docsection_list')
    else:
        form = DocumentSectionForm(instance=obj)
    return render(request, 'panel/object_form.html', {
        'form': form,
        'object': obj,
        'active_menu': 'docsections',
        'title': 'Редактировать раздел' if obj else 'Добавить раздел',
        'back_url': reverse('panel:docsection_list'),
    })


@staff_required
@require_POST
def docsection_delete(request, pk):
    obj = get_object_or_404(DocumentSection, pk=pk)
    obj.delete()
    messages.success(request, 'Раздел удалён')
    return redirect('panel:docsection_list')


# ── Меню ──────────────────────────────────────────────────────────────

@staff_required
def menu_list(request):
    return render(request, 'panel/menu_list.html', {
        'menu_items': MenuItem.objects.all(),
        'active_menu': 'menu',
        'title': 'Навигационное меню',
        'add_url': reverse('panel:menu_add'),
    })


@staff_required
def menu_edit(request, pk=None):
    obj = get_object_or_404(MenuItem, pk=pk) if pk else None
    section_pages = []
    if obj:
        section_pages = list(obj.get_children().filter(is_active=True).order_by('order', 'title'))
        if not section_pages and obj.page:
            section_pages = list(
                MenuItem.objects.filter(parent=obj.parent, is_active=True).order_by('order', 'title')
            ) if obj.parent else []

    if request.method == 'POST':
        form = MenuItemForm(request.POST, instance=obj)
        if form.is_valid():
            form.save()
            messages.success(request, 'Пункт меню сохранён')
            return redirect('panel:menu_list')
    else:
        form = MenuItemForm(instance=obj)

    return render(request, 'panel/menu_form.html', {
        'form': form,
        'object': obj,
        'section_pages': section_pages,
        'active_menu': 'menu',
        'title': 'Редактировать раздел меню' if obj else 'Добавить раздел меню',
        'back_url': reverse('panel:menu_list'),
    })


@staff_required
@require_POST
def menu_delete(request, pk):
    obj = get_object_or_404(MenuItem, pk=pk)
    obj.delete()
    messages.success(request, 'Пункт меню удалён')
    return redirect('panel:menu_list')


# ── Главная страница ──────────────────────────────────────────────────

@staff_required
def homepage_edit(request):
    homepage = HomePage.load()
    if request.method == 'POST':
        form = HomePageForm(request.POST, request.FILES, instance=homepage)
        if form.is_valid():
            form.save()
            messages.success(request, 'Главная страница обновлена')
            return redirect('panel:homepage')
    else:
        form = HomePageForm(instance=homepage)
    return render(request, 'panel/homepage_form.html', {
        'form': form,
        'active_menu': 'homepage',
        'title': 'Главная страница',
        'preview_url': '/',
    })


@staff_required
def quicklink_list(request):
    items = HomeQuickLink.objects.order_by('order', 'pk')
    return render(request, 'panel/quicklink_list.html', {
        'items': items,
        'total': items.count(),
        'active_menu': 'quicklinks',
        'title': 'Плитки главной',
    })


@staff_required
def quicklink_edit(request, pk=None):
    obj = get_object_or_404(HomeQuickLink, pk=pk) if pk else None
    if request.method == 'POST':
        form = HomeQuickLinkForm(request.POST, instance=obj)
        if form.is_valid():
            form.save()
            messages.success(request, 'Плитка сохранена')
            return redirect('panel:quicklink_list')
    else:
        form = HomeQuickLinkForm(instance=obj)
        if not obj:
            form.initial['order'] = next_quicklink_order()
            form.initial['style'] = free_quicklink_style()
    return render(request, 'panel/quicklink_form.html', {
        'form': form,
        'object': obj,
        'active_menu': 'quicklinks',
        'title': 'Редактировать плитку' if obj else 'Добавить плитку',
        'back_url': reverse('panel:quicklink_list'),
    })


@staff_required
@require_POST
def quicklink_delete(request, pk):
    obj = get_object_or_404(HomeQuickLink, pk=pk)
    obj.delete()
    messages.success(request, 'Плитка удалена')
    return redirect('panel:quicklink_list')


@staff_required
def homeblock_list(request):
    items = HomeBlock.objects.order_by('order')
    return render(request, 'panel/object_list.html', {
        'objects': items,
        'active_menu': 'homeblocks',
        'title': 'Блоки главной страницы',
        'add_url': reverse('panel:homeblock_add'),
        'edit_url_name': 'panel:homeblock_edit',
        'delete_url_name': 'panel:homeblock_delete',
        'columns': ['title', 'block_type', 'order', 'is_active'],
    })


@staff_required
def homeblock_edit(request, pk=None):
    obj = get_object_or_404(HomeBlock, pk=pk) if pk else None
    if request.method == 'POST':
        form = HomeBlockForm(request.POST, instance=obj)
        if form.is_valid():
            form.save()
            messages.success(request, 'Блок сохранён')
            return redirect('panel:homeblock_list')
    else:
        form = HomeBlockForm(instance=obj)
    return render(request, 'panel/object_form.html', {
        'form': form,
        'object': obj,
        'active_menu': 'homeblocks',
        'title': 'Редактировать блок' if obj else 'Добавить блок на главную',
        'back_url': reverse('panel:homeblock_list'),
    })


@staff_required
@require_POST
def homeblock_delete(request, pk):
    obj = get_object_or_404(HomeBlock, pk=pk)
    obj.delete()
    messages.success(request, 'Блок удалён')
    return redirect('panel:homeblock_list')


# ── Баннеры ───────────────────────────────────────────────────────────

@staff_required
def banner_list(request):
    items = Banner.objects.order_by('order')
    return render(request, 'panel/object_list.html', {
        'objects': items,
        'active_menu': 'banners',
        'title': 'Баннеры',
        'add_url': reverse('panel:banner_add'),
        'edit_url_name': 'panel:banner_edit',
        'delete_url_name': 'panel:banner_delete',
        'columns': ['title', 'order', 'is_active'],
    })


@staff_required
def banner_edit(request, pk=None):
    obj = get_object_or_404(Banner, pk=pk) if pk else None
    if request.method == 'POST':
        form = BannerForm(request.POST, request.FILES, instance=obj)
        if form.is_valid():
            form.save()
            messages.success(request, 'Баннер сохранён')
            return redirect('panel:banner_list')
    else:
        form = BannerForm(instance=obj)
    return render(request, 'panel/object_form.html', {
        'form': form,
        'object': obj,
        'active_menu': 'banners',
        'title': 'Редактировать баннер' if obj else 'Добавить баннер',
        'back_url': reverse('panel:banner_list'),
    })


@staff_required
@require_POST
def banner_delete(request, pk):
    obj = get_object_or_404(Banner, pk=pk)
    obj.delete()
    messages.success(request, 'Баннер удалён')
    return redirect('panel:banner_list')


# ── Галереи ───────────────────────────────────────────────────────────

@staff_required
def gallery_list(request):
    items = Gallery.objects.select_related('page').order_by('-created_at')
    return render(request, 'panel/object_list.html', {
        'objects': items,
        'active_menu': 'galleries',
        'title': 'Галереи',
        'add_url': reverse('panel:gallery_add'),
        'edit_url_name': 'panel:gallery_edit',
        'delete_url_name': 'panel:gallery_delete',
        'columns': ['title', 'page', 'is_active'],
    })


@staff_required
def gallery_edit(request, pk=None):
    gallery = get_object_or_404(Gallery, pk=pk) if pk else None

    if request.method == 'POST':
        form = GalleryForm(request.POST, instance=gallery)
        formset = GalleryImageFormSet(request.POST, request.FILES, instance=gallery) if gallery else None

        if form.is_valid():
            gallery = form.save()
            if not pk:
                formset = GalleryImageFormSet(request.POST, request.FILES, instance=gallery)
            if formset and _handle_formset(formset, request):
                messages.success(request, 'Галерея сохранена')
                return redirect('panel:gallery_edit', pk=gallery.pk)
            elif formset and not formset.is_valid():
                messages.error(request, 'Проверьте изображения галереи')
            else:
                messages.success(request, 'Галерея сохранена')
                return redirect('panel:gallery_edit', pk=gallery.pk)
    else:
        form = GalleryForm(instance=gallery)
        formset = GalleryImageFormSet(instance=gallery) if gallery else None

    return render(request, 'panel/gallery_form.html', {
        'form': form,
        'formset': formset,
        'object': gallery,
        'active_menu': 'galleries',
        'title': 'Редактировать галерею' if gallery else 'Добавить галерею',
        'back_url': reverse('panel:gallery_list'),
    })


@staff_required
@require_POST
def gallery_delete(request, pk):
    obj = get_object_or_404(Gallery, pk=pk)
    obj.delete()
    messages.success(request, 'Галерея удалена')
    return redirect('panel:gallery_list')


# ── Специальности ─────────────────────────────────────────────────────

@staff_required
def program_list(request):
    items = EducationalProgram.objects.select_related('page').order_by('order', 'code')
    return render(request, 'panel/object_list.html', {
        'objects': items,
        'active_menu': 'programs',
        'title': 'Образовательные программы',
        'add_url': reverse('panel:program_add'),
        'edit_url_name': 'panel:program_edit',
        'delete_url_name': 'panel:program_delete',
        'columns': ['code', 'title', 'page', 'is_active'],
    })


@staff_required
def program_edit(request, pk=None):
    program = get_object_or_404(EducationalProgram, pk=pk) if pk else None

    if request.method == 'POST':
        form = EducationalProgramForm(request.POST, request.FILES, instance=program)
        formset = AdmissionYearFormSet(request.POST, instance=program) if program else None

        if form.is_valid():
            is_new = program is None
            program = form.save()

            if is_new:
                messages.success(request, 'Программа создана')
                return redirect('panel:program_edit', pk=program.pk)

            if formset and _handle_formset(formset, request):
                messages.success(request, 'Программа сохранена')
                return redirect('panel:program_edit', pk=program.pk)
            elif formset and not formset.is_valid():
                messages.error(request, 'Проверьте годы поступления')
            else:
                messages.success(request, 'Программа сохранена')
                return redirect('panel:program_edit', pk=program.pk)
    else:
        form = EducationalProgramForm(instance=program)
        formset = AdmissionYearFormSet(instance=program) if program else None

    return render(request, 'panel/program_form.html', {
        'form': form,
        'formset': formset,
        'object': program,
        'active_menu': 'programs',
        'title': 'Редактировать программу' if program else 'Добавить программу',
        'back_url': reverse('panel:program_list'),
    })

@staff_required
@require_POST
def program_delete(request, pk):
    obj = get_object_or_404(EducationalProgram, pk=pk)
    obj.delete()
    messages.success(request, 'Программа удалена')
    return redirect('panel:program_list')


@staff_required
def program_docs(request, year_pk):
    year = get_object_or_404(AdmissionYear, pk=year_pk)
    if request.method == 'POST':
        formset = ProgramDocumentFormSet(request.POST, request.FILES, instance=year)
        if _handle_formset(formset, request):
            messages.success(request, 'Документы программы сохранены')
            return redirect('panel:program_docs', year_pk=year.pk)
    else:
        formset = ProgramDocumentFormSet(instance=year)

    return render(request, 'panel/program_docs_form.html', {
        'formset': formset,
        'year': year,
        'program': year.program,
        'active_menu': 'programs',
        'title': f'Документы: {year.program.title} ({year.year})',
        'back_url': reverse('panel:program_edit', kwargs={'pk': year.program.pk}),
    })


# ── Блоки контента ────────────────────────────────────────────────────

@staff_required
def block_list(request):
    items = ContentBlock.objects.select_related('page').order_by('page', 'order')
    page_filter = request.GET.get('page', '')
    if page_filter:
        items = items.filter(page_id=page_filter)
    pages = Page.objects.order_by('title')
    return render(request, 'panel/block_list.html', {
        'objects': items,
        'page_filter': page_filter,
        'pages': pages,
        'active_menu': 'blocks',
        'title': 'Блоки контента',
        'add_url': reverse('panel:block_add'),
    })


@staff_required
def block_edit(request, pk=None):
    obj = get_object_or_404(ContentBlock, pk=pk) if pk else None
    page_id = request.GET.get('page') or request.POST.get('page') or request.POST.get('return_page')
    if request.method == 'POST':
        form = ContentBlockForm(request.POST, instance=obj)
        if form.is_valid():
            block = form.save()
            messages.success(request, 'Блок сохранён')
            if page_id or block.page_id:
                return redirect('panel:page_edit', pk=page_id or block.page_id)
            return redirect('panel:block_list')
    else:
        form = ContentBlockForm(instance=obj)
        if not obj and page_id:
            form.initial['page'] = page_id
    back_url = reverse('panel:page_edit', kwargs={'pk': page_id}) if page_id else reverse('panel:block_list')
    return render(request, 'panel/object_form.html', {
        'form': form,
        'object': obj,
        'active_menu': 'blocks',
        'title': 'Редактировать блок' if obj else 'Добавить блок',
        'back_url': back_url,
    })


@staff_required
@require_POST
def block_delete(request, pk):
    obj = get_object_or_404(ContentBlock, pk=pk)
    obj.delete()
    messages.success(request, 'Блок удалён')
    return redirect('panel:block_list')


# ── Медиафайлы ────────────────────────────────────────────────────────

@staff_required
def media_library(request):
    from django.conf import settings

    uploaded = []
    media_root = settings.MEDIA_ROOT

    if request.method == 'POST' and request.FILES.get('file'):
        uploaded_file = request.FILES['file']
        subdir = request.POST.get('subdir', 'uploads')
        dest_dir = os.path.join(media_root, subdir)
        os.makedirs(dest_dir, exist_ok=True)
        filepath = os.path.join(dest_dir, uploaded_file.name)
        with open(filepath, 'wb+') as f:
            for chunk in uploaded_file.chunks():
                f.write(chunk)
        messages.success(request, f'Файл «{uploaded_file.name}» загружен')
        return redirect('panel:media')

    files = []
    if os.path.exists(media_root):
        for root, dirs, filenames in os.walk(media_root):
            for name in filenames:
                full_path = os.path.join(root, name)
                rel_path = os.path.relpath(full_path, media_root)
                url = settings.MEDIA_URL + rel_path.replace('\\', '/')
                ext = os.path.splitext(name)[1].lower()
                is_image = ext in ('.jpg', '.jpeg', '.png', '.gif', '.webp', '.svg')
                mtime = os.path.getmtime(full_path)
                files.append({
                    'name': name,
                    'path': rel_path,
                    'url': url,
                    'is_image': is_image,
                    'size': os.path.getsize(full_path),
                    'modified': datetime.fromtimestamp(mtime),
                })
        files.sort(key=lambda x: x['modified'], reverse=True)

    return render(request, 'panel/media.html', {
        'files': files,
        'active_menu': 'media',
        'title': 'Медиафайлы',
    })


@staff_required
@require_POST
def media_delete(request):
    from django.conf import settings

    rel_path = request.POST.get('path', '')
    if not rel_path or '..' in rel_path:
        messages.error(request, 'Некорректный путь')
        return redirect('panel:media')

    full_path = os.path.join(settings.MEDIA_ROOT, rel_path)
    if os.path.isfile(full_path):
        os.remove(full_path)
        messages.success(request, 'Файл удалён')
    else:
        messages.error(request, 'Файл не найден')
    return redirect('panel:media')


# ── Таблицы ───────────────────────────────────────────────────────────

@staff_required
def table_list(request):
    items = ContentTable.objects.order_by('title')
    return render(request, 'panel/object_list.html', {
        'objects': items,
        'active_menu': 'tables',
        'title': 'Таблицы',
        'add_url': reverse('panel:table_add'),
        'edit_url_name': 'panel:table_edit',
        'delete_url_name': 'panel:table_delete',
        'columns': ['title', 'slug', 'updated_at'],
    })


@staff_required
def table_edit(request, pk=None):
    obj = get_object_or_404(ContentTable, pk=pk) if pk else None
    if request.method == 'POST':
        form = ContentTableForm(request.POST, instance=obj)
        if form.is_valid():
            form.save()
            messages.success(request, 'Таблица сохранена')
            return redirect('panel:table_list')
    else:
        form = ContentTableForm(instance=obj)
    from .embed_utils import find_pages_using_table
    usage_pages = find_pages_using_table(obj) if obj else []
    return render(request, 'panel/table_form.html', {
        'form': form,
        'object': obj,
        'usage_pages': usage_pages,
        'active_menu': 'tables',
        'title': 'Редактировать таблицу' if obj else 'Добавить таблицу',
        'back_url': reverse('panel:table_list'),
    })


@staff_required
@require_POST
def table_delete(request, pk):
    obj = get_object_or_404(ContentTable, pk=pk)
    obj.delete()
    messages.success(request, 'Таблица удалена')
    return redirect('panel:table_list')


# ── Подвал ────────────────────────────────────────────────────────────

@staff_required
def footer_edit(request):
    homepage = HomePage.load()
    if request.method == 'POST':
        form = FooterForm(request.POST, instance=homepage)
        if form.is_valid():
            form.save()
            messages.success(request, 'Подвал обновлён')
            return redirect('panel:footer')
    else:
        form = FooterForm(instance=homepage)
    return render(request, 'panel/object_form.html', {
        'form': form,
        'active_menu': 'footer',
        'title': 'Подвал сайта',
        'back_url': reverse('panel:dashboard'),
    })


@staff_required
def api_table_snippet(request, pk):
    from .embed_utils import table_embed_placeholder_html, table_embed_tag
    table = get_object_or_404(ContentTable, pk=pk)
    return JsonResponse({
        'title': table.title,
        'slug': table.slug,
        'tag': table_embed_tag(table.slug),
        'html': table_embed_placeholder_html(table.slug, table.title),
    })


@staff_required
def api_document_snippet(request, pk):
    from .snippet_utils import document_snippet_html
    doc = get_object_or_404(Document, pk=pk)
    return JsonResponse({'title': doc.title, 'html': document_snippet_html(doc)})


@staff_required
def api_editor_snippets(request):
    tables = [
        {'id': t.pk, 'title': t.title, 'slug': t.slug}
        for t in ContentTable.objects.order_by('title')
    ]
    docs = []
    for d in Document.objects.filter(is_active=True).select_related('page').order_by('title')[:300]:
        url = d.external_url or (d.file.url if d.file and d.file.name else '')
        docs.append({
            'id': d.pk,
            'title': d.title,
            'url': url,
            'description': d.description,
            'file_size': d.file_size,
        })
    return JsonResponse({'tables': tables, 'documents': docs})


# ── Годы поступления ──────────────────────────────────────────────────

@staff_required
def admission_year_list(request):
    items = AdmissionYear.objects.select_related('program').order_by('program__order', '-year')
    return render(request, 'panel/admission_year_list.html', {
        'items': items,
        'active_menu': 'admission_years',
        'title': 'Годы поступления',
    })


# ── Пользователи ──────────────────────────────────────────────────────

def superuser_required(view_func):
    decorated = login_required(
        user_passes_test(lambda u: u.is_superuser)(view_func)
    )
    return decorated


@superuser_required
def user_list(request):
    users = User.objects.order_by('username')
    return render(request, 'panel/user_list.html', {
        'users': users,
        'active_menu': 'users',
        'title': 'Пользователи',
    })


@superuser_required
def user_edit(request, pk=None):
    obj = get_object_or_404(User, pk=pk) if pk else None
    if request.method == 'POST':
        form = PanelUserForm(request.POST, instance=obj, request_user=request.user)
        if form.is_valid():
            user = form.save()
            if not obj:
                messages.success(request, f'Пользователь «{user.username}» создан')
            else:
                messages.success(request, 'Пользователь сохранён')
            return redirect('panel:user_list')
    else:
        form = PanelUserForm(instance=obj, request_user=request.user)
        if not obj:
            form.fields['password'].required = True
            form.fields['password'].help_text = 'Обязателен для нового пользователя'
    return render(request, 'panel/object_form.html', {
        'form': form,
        'object': obj,
        'active_menu': 'users',
        'title': 'Редактировать пользователя' if obj else 'Добавить пользователя',
        'back_url': reverse('panel:user_list'),
    })


@superuser_required
@require_POST
def user_delete(request, pk):
    user = get_object_or_404(User, pk=pk)
    if user.pk == request.user.pk:
        messages.error(request, 'Нельзя удалить свой аккаунт')
        return redirect('panel:user_list')
    username = user.username
    user.delete()
    messages.success(request, f'Пользователь «{username}» удалён')
    return redirect('panel:user_list')
