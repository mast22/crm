from notifications.models import Notification
from django.views.generic.list import ListView
from django.views.generic.edit import UpdateView
from django.contrib.auth.mixins import UserPassesTestMixin
from django.contrib.messages.views import SuccessMessageMixin
from users.models import User
from django.shortcuts import reverse
from . import forms as f


class NotificationView(ListView):
    model = Notification

    def get_queryset(self):
        user = self.request.user
        return Notification.objects.filter(recipient=user)


class UserSettingsView(UserPassesTestMixin, UpdateView, SuccessMessageMixin):
    model = User
    form_class = f.UserSettingsForm
    template_name_suffix = '_settings_form'
    context_object_name = 'current_user'
    success_message = 'Настройки были сохранены'

    def get_success_url(self):
        user = self.request.user
        return reverse('users:account', args=(user.id,))

    def test_func(self):
        obj = self.get_object()
        user = self.request.user

        return obj == user
