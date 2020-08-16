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

# Вопросы:
# 1. Если все отклоняют заявку, то куда она попадает
# 2. Если заявка завершена, то куда она попадает

TASK_STATUS_CHOICES = (                             #   Проджект манагер    Тимлид
    (TaskStatuses.NEW, _('Новая')),                 #   Входящие                            На оценке
    (TaskStatuses.QUESTIONED, _('Есть вопросы')),   #   Входящая                            На оценке
    (TaskStatuses.RATED, _('Оцененная')),           #   Входящая                            На оценке
    (TaskStatuses.REJECTED, _('Отклоненная')),      #   Входящая                            На оценке
    (TaskStatuses.IN_PROGRESS, _('В работе')),      #   В работе                            В работе
    (TaskStatuses.COMPLETED, _('Завершена')),       #   В работе                            В работе
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