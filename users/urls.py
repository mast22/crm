from django.urls import path, include
from .views import NotificationView, mark_notifications_as_read
from django.views.generic.base import TemplateView
from . import views as v

app_name = 'users'
urlpatterns = [
    path('notifications', NotificationView.as_view(), name='notification-list'),
    path('mark-as-read', mark_notifications_as_read, name='mark-notifications-as-read'),
    path('rules/', TemplateView.as_view(template_name='users/rules.html'), name='rules'),
    path('<int:pk>/account/', v.UserSettingsView.as_view(), name='account'),
]