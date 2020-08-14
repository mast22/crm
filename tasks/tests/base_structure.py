from django.test import Client, TestCase
from os.path import join
from django.shortcuts import reverse
from common.preload import run_preload
from comments.models import Comment, CommentFile
from tasks.models import File, Task
from django.conf import settings


class BaseTaskTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        run_preload(add_users=True)

    def setUp(self):
        self.client = Client()

    def create_comment(self, creator, task: Task, parent: Comment=None):
        file_1 = join(settings.BASE_DIR, 'templates/base.html')
        file_2 = join(settings.BASE_DIR, 'templates/navbar.html')

        comment = Comment.objects.create(
            taks=task,
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