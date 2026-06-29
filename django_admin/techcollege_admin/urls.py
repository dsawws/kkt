from django.contrib import admin
from django.urls import path, include, re_path
from django.conf import settings
from django.conf.urls.static import static
from django.views.static import serve
from django.shortcuts import redirect
import os

FRONTEND_ROOT = os.path.join(str(settings.BASE_DIR.parent), 'frontend')
UPLOADS_ROOT = os.path.join(str(settings.BASE_DIR.parent), 'uploads')


def admin_redirect(request):
    return redirect('panel:dashboard')


urlpatterns = [
    path('panel/', include('cms.panel_urls')),
    path('admin/', admin_redirect),
    path('django-admin/', admin.site.urls),
    path('ckeditor/', include('ckeditor_uploader.urls')),
    path('', include('cms.urls', namespace='cms')),
    re_path(r'^frontend/(?P<path>.*)$', serve, {'document_root': FRONTEND_ROOT}),
    re_path(r'^uploads/(?P<path>.*)$', serve, {'document_root': UPLOADS_ROOT}),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

admin.site.site_header = "Админ-панель Техникума"
admin.site.site_title = "Техникум"
admin.site.index_title = "Управление сайтом"
