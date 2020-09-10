from .base_structure import BaseTaskTests
from django.urls import reverse
from users.models import User
from django.contrib.auth.models import Group
from ..models import Task
from ..const import WorkTypeChoices, TaskStatusTypes
from datetime import datetime, timedelta
from common.const import MANAGER_GROUP_NAME


class ProjectManagerTasksTests(BaseTaskTests):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.manager = User.objects.get(username='manager')
        cls.task = Task.objects.create(
            name='тестовый таск',
            phone='+79991568802',
            whats_app='+79991568802',
            author=cls.manager,
            email='email@email.com',
            text='Рандомный текст',
            wanted_deadline=datetime.now(),
        )

    def test_manager_can_view_create_task(self):
        self.client.force_login(user=self.manager)
        response = self.client.get(reverse('tasks:task-create'))
        self.assertEqual(
            response.status_code, 200, 'Страница создания заявки должна быть доступна'
        )

    def test_manager_can_view_task(self):
        self.client.force_login(user=self.manager)
        response = self.client.get(reverse('tasks:task-detail', args=(self.task.id,)))
        self.assertEqual(
            response.status_code, 200, 'Заявка должна быть доступная для просмотра'
        )

    def test_manager_cannot_put_to_work_without_performer_responses(self):
        self.client.force_login(user=self.manager)
        response = self.client.get(reverse('tasks:put-to-work', args=(self.task.id,)))
        self.assertRedirects(response, reverse('tasks:task-detail', args=(self.task.id,)), status_code=302, target_status_code=200)

    def test_manager_cannot_rate_task(self):
        self.client.force_login(user=self.manager)

        response = self.client.get(
            reverse('tasks:change-task-status', args=(self.task.id,))
        )

        self.assertRedirects(
            response,
            f"{reverse('login')}?next={reverse('tasks:change-task-status', args=(self.task.id,))}",
            status_code=302,
            target_status_code=200
        ) # Делает редирект на логин за другой аккаунт

        response = self.client.get(reverse('tasks:reject-task', args=(self.task.id,)))

        self.assertRedirects(
            response,
            f"{reverse('login')}?next={reverse('tasks:reject-task', args=(self.task.id,))}",
            status_code=302,
            target_status_code=200
        )  # Делает редирект на логин за другой аккаунт

    def test_manager_can_create_task(self):
        self.client.force_login(user=self.manager)
        task_name = 'тестовый таск'
        data = {
            'name': task_name,
            'phone': '+79991568802',
            'whats_app': '+79991568802',
            'email': 'email@email.com',
            'work_type': WorkTypeChoices.ARTICLE,
            'text': 'Рандомный текст',
            'wanted_deadline': datetime.now(),
        }
        response = self.client.post(reverse('tasks:task-create'), data=data)
        self.assertEqual(response.status_code, 200, 'Менеджер может создать заявку')
        self.assertTrue(Task.objects.filter(name=task_name).first())

    # Запускается последним
    def test_manager_can_delete_task(self):
        self.client.force_login(user=self.manager)
        response = self.client.get(reverse('tasks:delete-task', args=(self.task.id,)))
        self.assertEqual(
            response.status_code, 200, 'Заявка должна быть доступная для удаления'
        )

    def test_manager_cannot_view_not_his_task(self):
        manager_2 = User.objects.create_user(
            username='manager_2', email='pm2@gmail.com', password='wertlskdf123'
        )

        pms = Group.objects.get(name=MANAGER_GROUP_NAME)
        pms.user_set.add(manager_2)
        self.client.force_login(user=manager_2)
        response = self.client.get(reverse('tasks:task-detail', args=(self.task.id,)))
        self.assertEqual(response.status_code, 403)

    def test_manager_can_put_to_work(self):
        self.client.force_login(user=self.manager)
        response = self.client.get(reverse('tasks:put-to-work', args=(self.task.id,)))
        self.assertRedirects(response, reverse('tasks:task-detail', args=(self.task.id,)), status_code=302,
                             target_status_code=200)


class TeamLeaderTasksTests(BaseTaskTests):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.performer = User.objects.get(username='performer')
        cls.manager = User.objects.get(username='manager')
        cls.task = Task.objects.create(
            name='тестовый таск',
            phone='+79991568802',
            whats_app='+79991568802',
            author=cls.manager,
            email='email@email.com',
            text='Рандомный текст',
            wanted_deadline=datetime.now(),
        )

    def test_performer_cannot_create_task(self):
        self.client.force_login(user=self.performer)
        response = self.client.get(reverse('tasks:task-create'))
        self.assertEqual(
            response.status_code,
            403,
            'Страница создания заявки должна быть не доступна',
        )

    def test_performer_cannot_put_task_to_work(self):
        self.client.force_login(user=self.performer)
        response = self.client.get(reverse('tasks:put-to-work', args=(self.task.id,)))
        self.assertEqual(
            response.status_code, 302, 'ТЛ не может запускать в работу задачи'
        )

    # Запускать последним
    def test_performer_can_rate_task(self):
        self.client.force_login(user=self.performer)

        response = self.client.get(reverse('tasks:accept-task', args=(self.task.id,)))
        self.assertEqual(response.status_code, 200)


class BussinessProcessTestCase(BaseTaskTests):
    """
    Эти классы описывают то, что заявка правильно проходит этапы продажи
    """

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.performer = User.objects.get(username='performer')
        cls.manager = User.objects.get(username='manager')
        cls.performer_2 = cls.create_user(username='performer_2', group=cls.manager_group)
        cls.task = Task.objects.create(
            name='тестовый таск',
            phone='+79991568802',
            whats_app='+79991568802',
            author=cls.manager,
            email='email@email.com',
            text='Рандомный текст',
            wanted_deadline=datetime.now(),
        )

    def test_is_not_available_for_not_choosen_performers(self):
        self.create_task_status(task=self.task, performer=self.performer, status=TaskStatusTypes.ACCEPTED)

        url = reverse('tasks:task-detail', args=(self.task.id,))
        self.client.force_login(user=self.performer_2)
        response = self.client.get(url)

        self.assertEqual(response.status_code, 403)


    def test_task_status_is_not_approved_after_manager_comment(self):
        task_status = self.create_task_status(task=self.task, performer=self.performer, status=TaskStatusTypes.ACCEPTED)

        self.create_comment(self.manager, self.task)
        task_status.refresh_from_db()
        self.assertFalse(task_status.is_actual())

    def test_task_status_is_not_approved_after_72_hours(self):
        task_status = self.create_task_status(
            task=self.task,
            performer=self.performer,
            status=TaskStatusTypes.ACCEPTED,
        )
        # Обойдем auto_now=True
        self.task.task_statuses\
            .filter(id=task_status.id)\
            .update(last_modified=task_status.last_modified - timedelta(hours=80))

        task_status.refresh_from_db()
        self.assertFalse(task_status.is_actual())

    def test_notification_created_to_approve_status(self):
        self.assertTrue(False)
