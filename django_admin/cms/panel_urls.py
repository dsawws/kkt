from django.urls import path
from . import panel_views

app_name = 'panel'

urlpatterns = [
    path('login/', panel_views.panel_login, name='login'),
    path('logout/', panel_views.panel_logout, name='logout'),
    path('', panel_views.dashboard, name='dashboard'),

    # Страницы
    path('pages/', panel_views.page_list, name='page_list'),
    path('pages/add/', panel_views.page_edit, name='page_add'),
    path('pages/<int:pk>/edit/', panel_views.page_edit, name='page_edit'),
    path('pages/<int:pk>/delete/', panel_views.page_delete, name='page_delete'),
    path('organization/', panel_views.organization_hub, name='organization_hub'),

    # Новости
    path('news/', panel_views.news_list, name='news_list'),
    path('news/add/', panel_views.news_edit, name='news_add'),
    path('news/<int:pk>/edit/', panel_views.news_edit, name='news_edit'),
    path('news/<int:pk>/delete/', panel_views.news_delete, name='news_delete'),

    # Документы
    path('documents/', panel_views.document_list, name='document_list'),
    path('documents/add/', panel_views.document_edit, name='document_add'),
    path('documents/<int:pk>/edit/', panel_views.document_edit, name='document_edit'),
    path('documents/<int:pk>/delete/', panel_views.document_delete, name='document_delete'),

    # Разделы документов
    path('docsections/', panel_views.docsection_list, name='docsection_list'),
    path('docsections/add/', panel_views.docsection_edit, name='docsection_add'),
    path('docsections/<int:pk>/edit/', panel_views.docsection_edit, name='docsection_edit'),
    path('docsections/<int:pk>/delete/', panel_views.docsection_delete, name='docsection_delete'),

    # Меню
    path('menu/', panel_views.menu_list, name='menu_list'),
    path('menu/reorder/', panel_views.menu_reorder, name='menu_reorder'),
    path('menu/add/', panel_views.menu_edit, name='menu_add'),
    path('menu/<int:pk>/edit/', panel_views.menu_edit, name='menu_edit'),
    path('menu/<int:pk>/delete/', panel_views.menu_delete, name='menu_delete'),

    path('footer/', panel_views.footer_edit, name='footer'),

    path('tables/', panel_views.table_list, name='table_list'),
    path('tables/add/', panel_views.table_edit, name='table_add'),
    path('tables/<int:pk>/edit/', panel_views.table_edit, name='table_edit'),
    path('tables/<int:pk>/delete/', panel_views.table_delete, name='table_delete'),
    path('api/tables/<int:pk>/', panel_views.api_table_snippet, name='api_table_snippet'),
    path('api/documents/<int:pk>/', panel_views.api_document_snippet, name='api_document_snippet'),
    path('api/editor-snippets/', panel_views.api_editor_snippets, name='api_editor_snippets'),

    # Главная (скрыто из меню, доступ через страницы)
    path('homepage/', panel_views.homepage_edit, name='homepage'),
    path('quicklinks/', panel_views.quicklink_list, name='quicklink_list'),
    path('quicklinks/add/', panel_views.quicklink_edit, name='quicklink_add'),
    path('quicklinks/<int:pk>/edit/', panel_views.quicklink_edit, name='quicklink_edit'),
    path('quicklinks/<int:pk>/delete/', panel_views.quicklink_delete, name='quicklink_delete'),
    path('homeblocks/', panel_views.homeblock_list, name='homeblock_list'),
    path('homeblocks/add/', panel_views.homeblock_edit, name='homeblock_add'),
    path('homeblocks/<int:pk>/edit/', panel_views.homeblock_edit, name='homeblock_edit'),
    path('homeblocks/<int:pk>/delete/', panel_views.homeblock_delete, name='homeblock_delete'),

    # Баннеры
    path('banners/', panel_views.banner_list, name='banner_list'),
    path('banners/add/', panel_views.banner_edit, name='banner_add'),
    path('banners/<int:pk>/edit/', panel_views.banner_edit, name='banner_edit'),
    path('banners/<int:pk>/delete/', panel_views.banner_delete, name='banner_delete'),

    # Галереи
    path('galleries/', panel_views.gallery_list, name='gallery_list'),
    path('galleries/add/', panel_views.gallery_edit, name='gallery_add'),
    path('galleries/<int:pk>/edit/', panel_views.gallery_edit, name='gallery_edit'),
    path('galleries/<int:pk>/delete/', panel_views.gallery_delete, name='gallery_delete'),

    # Программы
    path('programs/', panel_views.program_list, name='program_list'),
    path('programs/add/', panel_views.program_edit, name='program_add'),
    path('programs/<int:pk>/edit/', panel_views.program_edit, name='program_edit'),
    path('programs/<int:pk>/delete/', panel_views.program_delete, name='program_delete'),
    path('programs/year/<int:year_pk>/docs/', panel_views.program_docs, name='program_docs'),

    path('admission-years/', panel_views.admission_year_list, name='admission_year_list'),

    path('users/', panel_views.user_list, name='user_list'),
    path('users/add/', panel_views.user_edit, name='user_add'),
    path('users/<int:pk>/edit/', panel_views.user_edit, name='user_edit'),
    path('users/<int:pk>/delete/', panel_views.user_delete, name='user_delete'),

    # Блоки
    path('blocks/', panel_views.block_list, name='block_list'),
    path('blocks/add/', panel_views.block_edit, name='block_add'),
    path('blocks/<int:pk>/edit/', panel_views.block_edit, name='block_edit'),
    path('blocks/<int:pk>/delete/', panel_views.block_delete, name='block_delete'),

    # Медиа
    path('media/', panel_views.media_library, name='media'),
    path('media/delete/', panel_views.media_delete, name='media_delete'),
]
