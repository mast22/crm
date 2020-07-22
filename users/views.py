from notifications.models import Notification
from django.views.generic.list import ListView


class NotificationView(ListView):
    model = Notification

    def get_queryset(self):
        user = self.request.user
        return Notification.objects.filter(recipient=user)
