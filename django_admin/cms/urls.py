from django.urls import path
from . import views

app_name = 'cms'

urlpatterns = [
    path('', views.index, name='index'),
    path('search/', views.search, name='search'),
    path('api/menu/', views.api_menu, name='api_menu'),
    path('api/homepage/', views.api_homepage, name='api_homepage'),
    path('api/page-api/<slug:slug>/', views.api_page, name='api_page'),
    path('page/<slug:slug>/', views.page_detail, name='page_detail'),
    path('news/', views.news_list, name='news_list'),
    path('news/<slug:slug>/', views.news_detail, name='news_detail'),
]
