from django.urls import path, include
from .views import NotificationView

app_name = 'users'
urlpatterns = [
    path('notifications', NotificationView.as_view(), name='notification-list'),
]