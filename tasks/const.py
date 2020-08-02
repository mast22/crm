from django.utils.translation import gettext as _

class TaskStatuses:
    NEW = 'new'
    RATED = 'rated'
    REJECTED = 'rejected'
    IN_PROGRESS = 'in-progress'
    QUESTIONED = 'questioned'
    COMPLETED = 'completed'


TASK_STATUS_CHOICES = (
    (TaskStatuses.NEW, _('Новая')),
    (TaskStatuses.QUESTIONED, _('Есть вопросы')),
    (TaskStatuses.RATED, _('Оцененная')),
    (TaskStatuses.REJECTED, _('Отклоненная')),
    (TaskStatuses.IN_PROGRESS, _('В работе')),
    (TaskStatuses.COMPLETED, _('Завершена')),
)


class WorkTypeChoices:
    TEST1 = 'test_1'
    TEST2 = 'test_2'


WORK_TYPE_CHOICES = (
    (WorkTypeChoices.TEST1, 'Тест1'),
    (WorkTypeChoices.TEST2, 'Тест2')
)


class DecisionChoices:
    REJECTED = 'rejected'
    TAKEN = 'taken'
    COMPLETED = 'completed'


DECISION_CHOICES = (
    (DecisionChoices.REJECTED, _('Отклоненная')),
    (DecisionChoices.TAKEN, _('Взята в рабту')),
    (DecisionChoices.COMPLETED, _('Завершена')),
)