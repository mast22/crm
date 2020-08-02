from django.contrib.auth.models import Group, Permission
from users.models import User
from django.conf import settings
from django.db import transaction
from .const import TEAM_LEADER_GROUP_NAME, PROJECT_MANAGER_GROUP_NAME

tl = None
pm = None

if settings.DEBUG:
    User.objects.create_superuser(
        username='admin', email='admin@admin.com', password='admin'
    )
    tl = User.objects.create_user(
        username='team_leader',
        email='team_leader@admin.com',
        password='admin',
        first_name='Team',
        last_name='Leader',
    )
    pm = User.objects.create_user(
        username='project_manager',
        email='project_manager.com',
        password='admin',
        first_name='Project',
        last_name='Manager',
    )

with transaction.atomic():
    team_leader_group = Group(name=TEAM_LEADER_GROUP_NAME,)

    project_manager_group = Group(name=PROJECT_MANAGER_GROUP_NAME)

    Group.objects.bulk_create([team_leader_group, project_manager_group])

    project_manager_permissions = [
        Permission.objects.get(codename='add_comment'),
        Permission.objects.get(codename='change_comment'),
        Permission.objects.get(codename='view_comment'),
        Permission.objects.get(codename='add_commentfile'),
        Permission.objects.get(codename='change_commentfile'),
        Permission.objects.get(codename='view_commentfile'),
        Permission.objects.get(codename='add_file'),
        Permission.objects.get(codename='change_file'),
        Permission.objects.get(codename='delete_file'),
        Permission.objects.get(codename='view_file'),
        Permission.objects.get(codename='add_task', content_type__app_label='tasks'),
        Permission.objects.get(codename='change_task', content_type__app_label='tasks'),
        Permission.objects.get(codename='delete_task', content_type__app_label='tasks'),
        Permission.objects.get(codename='view_task', content_type__app_label='tasks'),
        Permission.objects.get(codename='add_taskfile'),
        Permission.objects.get(codename='change_taskfile'),
        Permission.objects.get(codename='delete_taskfile'),
        Permission.objects.get(codename='view_taskfile'),
        Permission.objects.get(codename='can_put_to_work'),
    ]

    project_manager_group.permissions.set(project_manager_permissions)

    team_leader_permissions = [
        Permission.objects.get(codename='add_comment'),
        Permission.objects.get(codename='change_comment'),
        Permission.objects.get(codename='view_comment'),
        Permission.objects.get(codename='add_commentfile'),
        Permission.objects.get(codename='change_commentfile'),
        Permission.objects.get(codename='view_commentfile'),
        Permission.objects.get(codename='add_file'),
        Permission.objects.get(codename='change_file'),
        Permission.objects.get(codename='delete_file'),
        Permission.objects.get(codename='view_file'),
        Permission.objects.get(codename='view_task', content_type__app_label='tasks'),
        Permission.objects.get(codename='add_taskfile'),
        Permission.objects.get(codename='change_taskfile'),
        Permission.objects.get(codename='view_taskfile'),
        Permission.objects.get(codename='can_rate_task'),
    ]

    team_leader_group.permissions.set(team_leader_permissions)

    if tl and pm:
        tl.groups.add(team_leader_group)
        pm.groups.add(project_manager_group)
