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


class TaskStatusTypes:
    ACCEPTED = 'accepted'
    REJECTED = 'rejected'
    IN_WORK = 'in-work'


TASK_STATUS_TYPES_CHOICES = (
    (TaskStatusTypes.ACCEPTED, 'Принято'),
    (TaskStatusTypes.REJECTED, 'Отклонено'),
    (TaskStatusTypes.IN_WORK, 'Принят к работе'),
)