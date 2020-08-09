from .base_structure import BaseTaskTests
from django.urls import reverse
from users.models import User
from django.contrib.auth.models import Group
from ..models import Task
from ..const import WorkTypeChoices
from datetime import datetime
from common.const import PROJECT_MANAGER_GROUP_NAME


class ProjectManagerTasksTests(BaseTaskTests):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.project_manager = User.objects.get(username='project_manager')
        cls.task = Task.objects.create(
            name='тестовый таск',
            phone='+79991568802',
            whats_app='+79991568802',
            author=cls.project_manager,
            email='email@email.com',
            work_type=WorkTypeChoices.TEST1,
            address='Кукушкина 12',
            company='Компания',
            text='Рандомный текст',
            wanted_deadline=datetime.now(),
        )

    def test_project_manager_can_view_create_task(self):
        self.client.force_login(user=self.project_manager)
        response = self.client.get(reverse('tasks:task-create'))
        self.assertEqual(
            response.status_code, 200, 'Страница создания заявки должна быть доступна'
        )

    def test_project_manager_can_view_task(self):
        self.client.force_login(user=self.project_manager)
        response = self.client.get(reverse('tasks:task-detail', args=(self.task.id,)))
        self.assertEqual(
            response.status_code, 200, 'Заявка должна быть доступная для просмотра'
        )

    def test_project_manager_cannot_put_to_work_without_TL_responses(self):
        self.client.force_login(user=self.project_manager)
        response = self.client.get(reverse('tasks:put-to-work', args=(self.task.id,)))
        self.assertRedirects(response, reverse('tasks:task-detail', args=(self.task.id,)), status_code=302, target_status_code=200)

    def test_project_managet_cannot_rate_task(self):
        self.client.force_login(user=self.project_manager)

        response = self.client.get(reverse('tasks:accept-task', args=(self.task.id,)))
        self.assertEqual(response.status_code, 403)

        response = self.client.get(
            reverse('tasks:change-task-status', args=(self.task.id,))
        )
        self.assertEqual(response.status_code, 403)

        response = self.client.get(reverse('tasks:reject-task', args=(self.task.id,)))
        self.assertEqual(response.status_code, 302)

    def test_project_manager_can_create_task(self):
        self.client.force_login(user=self.project_manager)
        task_name = 'тестовый таск'
        data = {
            'name': task_name,
            'phone': '+79991568802',
            'whats_app': '+79991568802',
            'email': 'email@email.com',
            'work_type': WorkTypeChoices.TEST1,
            'address': 'Кукушкина 12',
            'company': 'Компания',
            'text': 'Рандомный текст',
            'wanted_deadline': datetime.now(),
        }
        response = self.client.post(reverse('tasks:task-create'), data=data)
        self.assertEqual(response.status_code, 200, 'ПМ может создать заявку')
        self.assertTrue(Task.objects.filter(name=task_name).first())

    # Запускается последним
    def test_project_manager_can_delete_task(self):
        self.client.force_login(user=self.project_manager)
        response = self.client.get(reverse('tasks:delete-task', args=(self.task.id,)))
        self.assertEqual(
            response.status_code, 200, 'Заявка должна быть доступная для удаления'
        )

    def test_project_manager_cannot_view_not_his_task(self):
        project_manager_2 = User.objects.create_user(
            username='project_manager_2', email='pm2@gmail.com', password='wertlskdf123'
        )

        pms = Group.objects.get(name=PROJECT_MANAGER_GROUP_NAME)
        pms.user_set.add(project_manager_2)
        self.client.force_login(user=project_manager_2)
        response = self.client.get(reverse('tasks:task-detail', args=(self.task.id,)))
        self.assertEqual(response.status_code, 403)


class TeamLeaderTasksTests(BaseTaskTests):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.team_leader = User.objects.get(username='team_leader')
        cls.project_manager = User.objects.get(username='project_manager')
        cls.task = Task.objects.create(
            name='тестовый таск',
            phone='+79991568802',
            whats_app='+79991568802',
            author=cls.project_manager,
            email='email@email.com',
            work_type=WorkTypeChoices.TEST1,
            address='Кукушкина 12',
            company='Компания',
            text='Рандомный текст',
            wanted_deadline=datetime.now(),
        )

    def test_team_leader_cannot_create_task(self):
        self.client.force_login(user=self.team_leader)
        response = self.client.get(reverse('tasks:task-create'))
        self.assertEqual(
            response.status_code,
            403,
            'Страница создания заявки должна быть не доступна',
        )

    def test_team_leader_cannot_put_task_to_work(self):
        self.client.force_login(user=self.team_leader)
        response = self.client.get(reverse('tasks:put-to-work', args=(self.task.id,)))
        self.assertEqual(
            response.status_code, 302, 'ТЛ не может запускать в работу задачи'
        )

    # Запускать последним
    def test_team_leader_can_rate_task(self):
        self.client.force_login(user=self.team_leader)

        response = self.client.get(reverse('tasks:accept-task', args=(self.task.id,)))
        self.assertEqual(response.status_code, 200)