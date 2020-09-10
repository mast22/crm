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


    def test_task_exists_for_author(self):
        class TestFilter(GroupFilterMixin, Filter):
            pass

        filter = TestFilter(self.manager)
        self.assertIn(self.task, filter.get_queryset(), 'У создавшего заявку ПМа должна быть заявка')

    def test_task_absent_for_not_author(self):
        class TestFilter(GroupFilterMixin, Filter):
            pass

        manager2 = self.create_user('manager2', self.manager_group)
        filter = TestFilter(manager2)
        self.assertNotIn(self.task, filter.get_queryset(), 'У другого ПМа должена отсутствовать заявка')

    def test_task_exists_for_performer(self):
        class TestFilter(GroupFilterMixin, Filter):
            pass

        performer2 = self.create_user('performer2', self.performer_group)
        filter = TestFilter(performer2)
        self.assertIn(self.task, filter.get_queryset(), '')

        performer2.delete()
        performer2 = None

    def test_task_absent_for_other_performers_when_its_in_progress(self):
        class TestFilter(GroupFilterMixin, Filter):
            pass

        performer2 = self.create_user('performer2', self.performer_group)

        self.task.status = TaskStatuses.IN_PROGRESS
        self.task.save()

        task_status = TaskStatus.objects.create(
            task=self.task,
            user=self.performer,
            type=TaskStatusTypes.ACCEPTED,
            price=10000,
            deadline=datetime.now(),
        )

        filter = TestFilter(performer2)
        self.assertNotIn(self.task, filter.get_queryset(), 'Исполнителям видны все заявки')

        performer2.delete()
        performer2 = None



