from django.contrib import admin
from django.utils.html import format_html
from mptt.admin import MPTTModelAdmin, DraggableMPTTAdmin
from .models import (
    MenuItem, Page, ContentBlock, Document,
    HomePage, Gallery, GalleryImage, Banner, News
)


@admin.register(MenuItem)
class MenuItemAdmin(DraggableMPTTAdmin):
    list_display = ('tree_actions', 'indented_title', 'slug', 'page', 'is_active', 'order')
    list_display_links = ('indented_title',)
    list_filter = ('is_active',)
    search_fields = ('title', 'slug')
    prepopulated_fields = {'slug': ('title',)}
    
    fieldsets = (
        ('Основная информация', {
            'fields': ('title', 'slug', 'parent', 'page')
        }),
        ('Настройки', {
            'fields': ('order', 'is_active')
        }),
    )


class ContentBlockInline(admin.TabularInline):
    model = ContentBlock
    extra = 1
    fields = ('block_type', 'title', 'content', 'order', 'is_active')
    ordering = ['order']


class DocumentInline(admin.TabularInline):
    model = Document
    extra = 1
    fields = ('category', 'title', 'file', 'order', 'is_active')
    ordering = ['category', 'order']


@admin.register(Page)
class PageAdmin(admin.ModelAdmin):
    list_display = ('title', 'parent', 'slug', 'is_published', 'show_in_menu', 'updated_at')
    list_filter = ('is_published', 'show_in_menu', 'parent', 'created_at')
    search_fields = ('title', 'slug', 'description', 'content')
    prepopulated_fields = {'slug': ('title',)}
    inlines = [ContentBlockInline, DocumentInline]
    
    fieldsets = (
        ('Основная информация', {
            'fields': ('title', 'slug', 'parent', 'description', 'content')
        }),
        ('Настройки публикации', {
            'fields': ('is_published', 'show_in_menu')
        }),
        ('SEO', {
            'fields': ('meta_title', 'meta_description', 'meta_keywords'),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.prefetch_related('blocks', 'documents')


@admin.register(ContentBlock)
class ContentBlockAdmin(admin.ModelAdmin):
    list_display = ('page', 'block_type', 'title', 'order', 'is_active', 'created_at')
    list_filter = ('block_type', 'is_active', 'page')
    search_fields = ('title', 'content', 'page__title')
    list_editable = ('order', 'is_active')
    
    fieldsets = (
        ('Основная информация', {
            'fields': ('page', 'block_type', 'title', 'content')
        }),
        ('Настройки', {
            'fields': ('order', 'is_active')
        }),
    )


@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'page', 'file_size', 'download_link', 'is_active', 'created_at')
    list_filter = ('category', 'is_active', 'page', 'created_at')
    search_fields = ('title', 'description', 'page__title')
    list_editable = ('is_active',)
    
    fieldsets = (
        ('Основная информация', {
            'fields': ('page', 'category', 'title', 'description', 'file')
        }),
        ('Настройки', {
            'fields': ('order', 'is_active')
        }),
    )
    
    def download_link(self, obj):
        if obj.file and obj.file.name:
            return format_html(
                '<a href="{}" target="_blank">Скачать</a>',
                obj.file.url
            )
        return '—'
    download_link.short_description = 'Файл'


@admin.register(News)
class NewsAdmin(admin.ModelAdmin):
    list_display = ('title', 'tag', 'is_published', 'created_at')
    list_filter = ('is_published', 'tag', 'created_at')
    search_fields = ('title', 'excerpt', 'content')
    prepopulated_fields = {'slug': ('title',)}
    list_editable = ('is_published',)
    fieldsets = (
        ('Основная информация', {
            'fields': ('title', 'slug', 'tag', 'excerpt', 'content', 'image')
        }),
        ('Публикация', {
            'fields': ('is_published',)
        }),
    )


@admin.register(Banner)
class BannerAdmin(admin.ModelAdmin):
    list_display = ('title', 'preview', 'url', 'order', 'is_active')
    list_editable = ('order', 'is_active')
    fieldsets = (
        ('Баннер', {'fields': ('title', 'image', 'url')}),
        ('Настройки', {'fields': ('order', 'is_active')}),
    )

    def preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="height:40px;">', obj.image.url)
        return '—'
    preview.short_description = 'Превью'


@admin.register(HomePage)
class HomePageAdmin(admin.ModelAdmin):
    fieldsets = (
        ('Приветствие', {
            'fields': ('welcome_title', 'welcome_text')
        }),
        ('Директор', {
            'fields': ('director_name', 'director_position', 'director_image', 'director_message')
        }),
        ('Слайдер', {
            'fields': ('slider_title', 'slider_text', 'slider_image')
        }),
    )
    
    def has_add_permission(self, request):
        return not HomePage.objects.exists()
    
    def has_delete_permission(self, request, obj=None):
        return False


class GalleryImageInline(admin.TabularInline):
    model = GalleryImage
    extra = 3
    fields = ('image', 'title', 'description', 'order')
    ordering = ['order']


@admin.register(Gallery)
class GalleryAdmin(admin.ModelAdmin):
    list_display = ('title', 'page', 'image_count', 'is_active', 'created_at')
    list_filter = ('is_active', 'page', 'created_at')
    search_fields = ('title', 'description', 'page__title')
    inlines = [GalleryImageInline]
    
    fieldsets = (
        ('Основная информация', {
            'fields': ('page', 'title', 'description')
        }),
        ('Настройки', {
            'fields': ('is_active',)
        }),
    )
    
    def image_count(self, obj):
        return obj.images.count()
    image_count.short_description = 'Количество изображений'


@admin.register(GalleryImage)
class GalleryImageAdmin(admin.ModelAdmin):
    list_display = ('thumbnail', 'title', 'gallery', 'order', 'created_at')
    list_filter = ('gallery', 'created_at')
    search_fields = ('title', 'description', 'gallery__title')
    list_editable = ('order',)
    
    fieldsets = (
        ('Основная информация', {
            'fields': ('gallery', 'image', 'title', 'description')
        }),
        ('Настройки', {
            'fields': ('order',)
        }),
    )
    
    def thumbnail(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" style="width: 50px; height: 50px; object-fit: cover;" />',
                obj.image.url
            )
        return '-'
    thumbnail.short_description = 'Превью'
