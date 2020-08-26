from django.contrib.auth.models import AbstractUser
from django.contrib.auth.models import Group
from django.db import models as m
from common.const import PERFORMER_GROUP_NAME, MANAGER_GROUP_NAME
from tasks.models import WorkType, WorkDirection

class User(AbstractUser):
    work_types = m.ManyToManyField(WorkType)
    work_directions = m.ManyToManyField(WorkDirection)
    phone = m.CharField(max_length=120, blank=True, null=True)

    def is_performer(self, user=None):
        return Group.objects.filter(
            name=PERFORMER_GROUP_NAME, user=(user or self)
        ).exists()

    def is_manager(self, user=None):
        return Group.objects.filter(
            name=MANAGER_GROUP_NAME, user=(user or self)
        ).exists()
