from django.utils.translation import gettext as _

class TaskStatuses:
    NEW = 'new'
    RATED = 'rated'
    REJECTED = 'rejected'
    IN_PROGRESS = 'in-progress'


TASK_STATUS_CHOICES = (
    (TaskStatuses.NEW, _('Новая')),
    (TaskStatuses.RATED, _('Оцененная')),
    (TaskStatuses.REJECTED, _('Отклоненная')),
    (TaskStatuses.IN_PROGRESS, _('В работе')),
)

class WorkTypeChoices:
    TEST1 = 'test_1'
    TEST2 = 'test_2'

WORK_TYPE_CHOICES = (
    (WorkTypeChoices.TEST1, 'Тест1'),
    (WorkTypeChoices.TEST2, 'Тест2')
)