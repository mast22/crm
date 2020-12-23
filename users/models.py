from django.contrib.auth.models import AbstractUser
from django.contrib.auth.models import Group
from django.db import models as m
from common.const import PERFORMER_GROUP_NAME, MANAGER_GROUP_NAME
from tasks.models import WorkType, WorkDirection
from .const import ROLE_CHOICES, Role

class User(AbstractUser):
    work_types = m.ManyToManyField(WorkType)
    work_directions = m.ManyToManyField(WorkDirection)
    phone = m.CharField(max_length=120, blank=True, null=True)
    role = m.CharField(choices=ROLE_CHOICES, max_length=15)

    def is_performer(self, user=None) -> bool:
        if user:
            return user.role == Role.performer
        return self.role == Role.performer

    def is_manager(self, user=None):
        if user:
            return user.role == Role.manager
        return self.role == Role.manager
