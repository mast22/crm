from .base_structure import BaseTaskTests
from users.models import User
from ..models import Task, File
from ..const import WorkTypeChoices
from datetime import datetime
from comments.models import Comment


class FileManagmentTestCase(BaseTaskTests):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.manager = User.objects.get(username='manager')
        cls.performer = User.objects.get(username='performer')
        cls.task = Task.objects.create(
            name='тестовый таск',
            phone='+79991568802',
            whats_app='+79991568802',
            author=cls.manager,
            email='email@email.com',
            text='Рандомный текст',
            wanted_deadline=datetime.now(),
        )

    def test_can_comment(self):
        response = self.create_comment_view(self.manager, self.task)
        self.assertEqual(response.status_code, 302) # Redirect значит комментарий создан
        self.assertEqual(Comment.objects.count(), 1)
        self.assertEqual(File.objects.count(), 2)

        response = self.create_comment_view(self.performer, self.task)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Comment.objects.count(), 2)
        self.assertEqual(File.objects.count(), 4)


    def test_file_cant_be_deleted_only_by_creator(self):
        response = self.create_comment_view(self.manager, self.task)
        file = Comment.objects.first().files.first()
        response = self.delete_file_view(self.performer, file)
        self.assertEqual(response.status_code, 403) # Запрещенно

        response = self.delete_file_view(self.manager, file)
        self.assertEqual(response.status_code, 302) # Редирект - успех

    def test_file_cant_be_deleted_by_creator_if_task_overriden(self):
        self.create_comment_view(self.manager, self.task)
        file = Comment.objects.first().files.first() # Файл для удаления
        self.create_comment_view(self.performer, self.task) # Комментарий другого пользователя
        response = self.delete_file_view(self.manager, file) # Пытаемся удалить
        self.assertEqual(response.status_code, 403)  # Запрещенно
