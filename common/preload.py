from users.models import User
from users.const import Role
from django.db import transaction
from tasks.models import WorkType, WorkDirection

def run_preload(add_users: bool):
    performer = None
    manager = None

    with transaction.atomic():
        WorkType.objects.bulk_create([
            WorkType(name='Тип работы 1'),
            WorkType(name='Тип работы 2'),
            WorkType(name='Тип работы 3'),
            WorkType(name='Тип работы 4'),
            WorkType(name='Тип работы 5'),
            WorkType(name='Тип работы 6'),
        ])

        WorkDirection.objects.bulk_create([
            WorkDirection(name='Направление работы 1'),
            WorkDirection(name='Направление работы 2'),
            WorkDirection(name='Направление работы 3'),
            WorkDirection(name='Направление работы 4'),
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
                role=Role.performer
            )
            manager = User.objects.create_user(
                username='manager',
                email='manager@gmail.com',
                password='admin',
                first_name='manager',
                role=Role.manager
            )
            performer2 = User.objects.create_user(
                username='performer2',
                email='performer2@admin.com',
                password='admin',
                first_name='performer2',
                role=Role.performer
            )