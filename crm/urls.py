from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from django.urls import path, include
from django.views.generic import TemplateView
import notifications.urls



urlpatterns = [
    path('', TemplateView.as_view(template_name="home.html"), name='home'),
    path('admin/', admin.site.urls),
    path('tasks/', include('tasks.urls')),
    path('comments/', include('comments.urls')),
    path('accounts/', include('django.contrib.auth.urls')),
    path(
        'inbox/notifications/', include(notifications.urls, namespace='notifications'),
    ),
    path('users/', include('users.urls')),
    path(
        'accounts/profile/',
        TemplateView.as_view(template_name="profile.html"),
        name='profile',
    ),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
