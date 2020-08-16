from .base_structure import BaseTaskTests
from users.models import User
from ..models import Task, TaskStatus, TaskStatusTypes
from ..const import TaskStatuses
from ..const import WorkTypeChoices
from datetime import datetime
from tasks.views import GroupFilterMixin


class Filter:
    """dependency injection"""
    class request:
        pass

    def __init__(self, user):
        self.request.user = user

    def get_queryset(self):
        return Task.objects.all()




class FilteringTasksTests(BaseTaskTests):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.project_manager = User.objects.get(username='project_manager')
        cls.team_leader = User.objects.get(username='team_leader')
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

    def test_task_exists_for_author(self):
        class TestFilter(GroupFilterMixin, Filter):
            pass

        filter = TestFilter(self.project_manager)
        self.assertIn(self.task, filter.get_queryset(), 'У создавшего заявку ПМа должна быть заявка')

    def test_task_absent_for_not_author(self):
        class TestFilter(GroupFilterMixin, Filter):
            pass

        project_manager2 = self.create_user('project_manager2', self.PM_group)
        filter = TestFilter(project_manager2)
        self.assertNotIn(self.task, filter.get_queryset(), 'У другого ПМа должена отсутствовать заявка')

    def test_task_exists_for_team_leader(self):
        class TestFilter(GroupFilterMixin, Filter):
            pass

        team_leader2 = self.create_user('team_leader2', self.TL_group)
        filter = TestFilter(team_leader2)
        self.assertIn(self.task, filter.get_queryset(), '')

        team_leader2.delete()
        team_leader2 = None

    def test_task_absent_for_other_team_leaders_when_its_in_progress(self):
        class TestFilter(GroupFilterMixin, Filter):
            pass

        team_leader2 = self.create_user('team_leader2', self.TL_group)

        self.task.status = TaskStatuses.IN_PROGRESS
        self.task.save()

        task_status = TaskStatus.objects.create(
            task=self.task,
            user=self.team_leader,
            type=TaskStatusTypes.ACCEPTED,
            price=10000,
            deadline=datetime.now(),
        )

        filter = TestFilter(team_leader2)
        self.assertNotIn(self.task, filter.get_queryset(), 'ТЛам видны все заявки')

        team_leader2.delete()
        team_leader2 = None



