from django.contrib.auth.models import Group, Permission
from users.models import User
from django.conf import settings
from django.db import transaction
from .const import PERFORMER_GROUP_NAME, MANAGER_GROUP_NAME
from tasks.models import WorkType, WorkDirection

def run_preload(add_users: bool):
    performer = None
    manager = None

    with transaction.atomic():
        WorkType.objects.bulk_create([
            WorkType(name='Дипломная работа'),
            WorkType(name='Магистерская диссертация'),
            WorkType(name='Научная статья'),
            WorkType(name='Отчёт по практике'),
            WorkType(name='Доклад'),
            WorkType(name='Презентация'),
        ])

        WorkDirection.objects.bulk_create([
            WorkDirection(name='Менеджмент'),
            WorkDirection(name='Маркетинг'),
            WorkDirection(name='Нефтяная промышленность'),
            WorkDirection(name='Программирование'),
        ])

        if add_users:
            User.objects.create_superuser(
                username='admin', email='admin@admin.com', password='admin'
            )
            performer = User.objects.create_user(
                username='performer',
                email='performer@admin.com',
                password='admin',
                first_name='performer',
            )
            manager = User.objects.create_user(
                username='manager',
                email='manager@gmail.com',
                password='admin',
                first_name='manager',
            )
            performer2 = User.objects.create_user(
                username='performer2',
                email='performer2@admin.com',
                password='admin',
                first_name='performer2',
            )

        with transaction.atomic():
            team_leader_group = Group.objects.create(name=PERFORMER_GROUP_NAME, )
            project_manager_group = Group.objects.create(
                name=MANAGER_GROUP_NAME
            )

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
                Permission.objects.get(
                    codename='add_task', content_type__app_label='tasks'
                ),
                Permission.objects.get(
                    codename='change_task', content_type__app_label='tasks'
                ),
                Permission.objects.get(
                    codename='delete_task', content_type__app_label='tasks'
                ),
                Permission.objects.get(
                    codename='view_task', content_type__app_label='tasks'
                ),
                Permission.objects.get(codename='add_taskfile'),
                Permission.objects.get(codename='change_taskfile'),
                Permission.objects.get(codename='delete_taskfile'),
                Permission.objects.get(codename='view_taskfile'),
                Permission.objects.get(codename='can_put_to_work'),
                Permission.objects.get(codename='can_see_extra'),
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
                Permission.objects.get(
                    codename='view_task', content_type__app_label='tasks'
                ),
                Permission.objects.get(codename='add_taskfile'),
                Permission.objects.get(codename='change_taskfile'),
                Permission.objects.get(codename='view_taskfile'),
                Permission.objects.get(codename='can_rate_task'),
            ]

            team_leader_group.permissions.set(team_leader_permissions)

            if performer and manager:
                performer.groups.add(team_leader_group)
                performer2.groups.add(team_leader_group)
                manager.groups.add(project_manager_group)

            performer.work_types.set([WorkType.objects.first(), WorkType.objects.last()])
