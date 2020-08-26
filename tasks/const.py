from django.utils.translation import gettext as _

class TaskStatuses:
    NEW = 'new'
    RATED = 'rated'
    REJECTED = 'rejected'
    IN_PROGRESS = 'in-progress'
    QUESTIONED = 'questioned'
    COMPLETED = 'completed'

# Тимлид - на оценкеВходящая, в работе
#
# На оценке - созданные ПМами заявки выбираются тим лидами
# В работе - заявки, которые выполнят данный Тимлид
#
# ПМ - входящие, в работе
#
# Входящие - созданные заявки, которые не были отданы в работу
# В работе - заявки, отданные в работе

TASK_STATUS_CHOICES = (
    (TaskStatuses.NEW, _('Новая')),
    (TaskStatuses.QUESTIONED, _('Есть вопросы')),
    (TaskStatuses.RATED, _('Оцененная')),
    (TaskStatuses.REJECTED, _('Отклоненная')),
    (TaskStatuses.IN_PROGRESS, _('В работе')),
    (TaskStatuses.COMPLETED, _('Завершена')),
)


class WorkTypeChoices:
    THESIS = 'thesis'
    MASTERS = 'masters'
    ARTICLE = 'article'
    PRACTICE = 'practice'
    REPORT = 'report'
    PRESENTATION = 'presentation'


WORK_TYPE_CHOICES = (
    (WorkTypeChoices.THESIS, 'Дипломная работа'),
    (WorkTypeChoices.MASTERS, 'Магистерская диссертация'),
    (WorkTypeChoices.ARTICLE, 'Научная статья'),
    (WorkTypeChoices.PRACTICE, 'Отчёт по практике'),
    (WorkTypeChoices.REPORT, 'Доклад'),
    (WorkTypeChoices.PRESENTATION, 'Презентация'),
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