from django.contrib.auth.models import AbstractUser
from django.contrib.auth.models import Group
from common.const import TEAM_LEADER_GROUP_NAME, PROJECT_MANAGER_GROUP_NAME


class User(AbstractUser):
    def is_team_leader(self, user=None):
        return Group.objects.filter(
            name=TEAM_LEADER_GROUP_NAME, user=(user or self)
        ).exists()

    def is_project_mangager(self, user=None):
        return Group.objects.filter(
            name=PROJECT_MANAGER_GROUP_NAME, user=(user or self)
        ).exists()
