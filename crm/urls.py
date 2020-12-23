from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from django.urls import path, include
import notifications.urls


urlpatterns = [
    path('', include('tasks.urls')),
    path('admin/', admin.site.urls),
    path('comments/', include('comments.urls')),
    path('accounts/', include('django.contrib.auth.urls')),
    path(
        'inbox/notifications/', include(notifications.urls, namespace='notifications'),
    ),
    path('users/', include('users.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)