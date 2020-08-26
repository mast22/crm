from notifications.models import Notification
from django.views.generic.list import ListView
from django.views.generic.edit import UpdateView
from users.models import User
from . import forms as f


class NotificationView(ListView):
    model = Notification

    def get_queryset(self):
        user = self.request.user
        return Notification.objects.filter(recipient=user)


class UserSettingsView(UpdateView):
    model = User
    form_class = f.UserSettingsForm
    template_name_suffix = '_settings_form'

# def user_settings(request):
#     user = request.user
#     pass