from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from django.urls import path, include
from django.views.generic import TemplateView
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
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
