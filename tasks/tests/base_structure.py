from django.test import Client, TestCase
from django.utils import timezone
from datetime import timedelta
from os.path import join
import random, string
from django.shortcuts import reverse
from common.preload import run_preload
from comments.models import Comment, CommentFile
from tasks.models import File, Task, TaskStatus
from users.models import Group, User
from django.conf import settings
from common.const import PERFORMER_GROUP_NAME, MANAGER_GROUP_NAME


class BaseTaskTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        run_preload(add_users=True)

        cls.performer_group = Group.objects.get(name=PERFORMER_GROUP_NAME)
        cls.manager_group = Group.objects.get(name=MANAGER_GROUP_NAME)

    def setUp(self):
        self.client = Client()

    def create_comment(self, creator, task: Task, parent: Comment=None):
        file_1 = join(settings.BASE_DIR, 'templates/base.html')
        file_2 = join(settings.BASE_DIR, 'templates/navbar.html')

        comment = Comment.objects.create(
            task=task,
            author=creator,
            text='Lorem ipsum dolor sit amet',
            parent=parent
        )

        CommentFile.objects.create(file=File.objects.create(
            file=file_1,
            comment='Comment',
        ), comment=comment)

        CommentFile.objects.create(file=File.objects.create(
            file=file_2,
            comment='Comment_2'
        ), comment=comment)

    def create_comment_view(self, creator, task: Task, parent: Comment=None):
        file_1 = join(settings.BASE_DIR, 'templates/base.html')
        file_2 = join(settings.BASE_DIR, 'templates/navbar.html')

        if parent is None:
            url = reverse('comments:comment-create', args=(task.id,))
        else:
            url = reverse('comments:comment-reply', args=(task.id, parent.id))

        self.client.force_login(user=creator)
        with open(file_1) as file_1_open, open(file_2) as file_2_open:
            data = {'text': 'Lorem ipsum', 'files': [file_1_open, file_2_open]}
            response = self.client.post(url, data=data)

        return response

    def delete_file_view(self, deleter, file):
        url = reverse('tasks:delete-file', args=(file.id,))
        self.client.force_login(user=deleter)
        response = self.client.delete(url)

        return response

    @classmethod
    def random_string(cls, length):
        return ''.join(random.choice(string.ascii_lowercase + string.digits) for _ in range(length))

    @classmethod
    def create_user(cls, username: str, group: Group):
        """Создаёт пользователя, возвращает его и устанавливает аттрибутом """
        user = User.objects.create_user(
            username,
            email=f'{cls.random_string(5)}@mail.com',
            password=cls.random_string(10)
        )

        group.user_set.add(user)

        return user

    def create_task_status(self, task: Task, performer: User, status: str):
        return TaskStatus.objects.create(
            task=task,
            user=performer,
            type=status,
            price=1000,
            deadline=timezone.now() + timedelta(hours=128),
        )