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
