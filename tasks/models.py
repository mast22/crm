from django.db import models as m
from django.utils import timezone
from datetime import timedelta
from django.urls import reverse
from django.dispatch import receiver
from django.conf import settings
from django.forms.models import model_to_dict
from common.const import MANAGER_GROUP_NAME
from .const import (
    TaskStatuses,
    TASK_STATUS_CHOICES,
    TASK_STATUS_TYPES_CHOICES,
    TaskStatusTypes,
)


class WorkType(m.Model):
    name = m.CharField(max_length=100)

    def __str__(self):
        return self.name


class WorkDirection(m.Model):
    name = m.CharField(max_length=100)

    def __str__(self):
        return self.name


class Task(m.Model):
    customer_name = m.CharField('Имя клиента', max_length=150)
    name = m.CharField('Основная идея', max_length=150)
    text = m.TextField('Исходные данные и требования')
    author = m.ForeignKey(settings.AUTH_USER_MODEL, on_delete=m.CASCADE)
    created_at = m.DateTimeField(auto_now_add=True)
    status = m.CharField(
        'Статус', choices=TASK_STATUS_CHOICES, default=TaskStatuses.NEW, max_length=11
    )
    wanted_deadline = m.DateField('Желаемый срок', null=True)
    teacher_name = m.CharField('ФИО руководителя', null=True, max_length=100)
    phone = m.CharField('Номер телефона', max_length=150)
    whats_app = m.CharField('What\'s App', max_length=150)
    work_type = m.ForeignKey(WorkType, on_delete=m.SET_NULL, null=True, verbose_name='Тип работы')
    work_direction = m.ForeignKey(WorkDirection, on_delete=m.SET_NULL, null=True, verbose_name='Направление')
    email = m.EmailField('Электронная почта')
    address = m.CharField('Адрес', max_length=150)
    company = m.CharField('Компания', max_length=150)
    notes = m.TextField('Заметки', blank=True)
    prepayment_received = m.BooleanField('Предоплата внесена', default=False)

    class Meta:
        ordering = ['-created_at']
        permissions = (
            ('can_rate_task', 'Может оценить заявку'),
            ('can_put_to_work', 'Может отдать в работу'),
            ('can_see_extra', 'Может смотреть дополнительную информацию'),
        )

    def get_absolute_url(self):
        return reverse('task-detail', kwargs={'pk': self.pk})

    def can_be_edited(self):
        """
        Решаем если можно изменять заявку.
        Заявку нельзя изменять если:
        1. Она уже завершена или в прогрессе
        """
        return self.status in [TaskStatuses.COMPLETED, TaskStatuses.IN_PROGRESS]


class TaskStatus(m.Model):
    task = m.ForeignKey(Task, on_delete=m.CASCADE, related_name='task_statuses')
    user = m.ForeignKey("users.User", on_delete=m.CASCADE, related_name='task_statuses')
    last_modified = m.DateTimeField(auto_now=True)
    type = m.CharField(choices=TASK_STATUS_TYPES_CHOICES, max_length=8)
    price = m.DecimalField(decimal_places=2, max_digits=10, null=True)
    deadline = m.DateField(null=True)
    approved = m.BooleanField(default=True)

    def is_rejected(self) -> bool:
        return (
            self.type == TaskStatusTypes.REJECTED
            and self.deadline is None
            and self.price is None
        )

    def is_actual(self) -> bool:
        # Если решение подтверждено, то она актуально
        # Главное не забыть правильно его отменять - менять на False
        if not self.approved:
            return False
        # Если она не подтверждена и прошло более 72 часов с выставления заявки, то проверяем актуальность
        if self.last_modified + timedelta(hours=72) < timezone.now():
            return False
        # Если после выставления решения были комментарии от менеджера, то заявка не актуально
        if self.task.comments.filter(author__groups__name=MANAGER_GROUP_NAME, created_at__gt=self.last_modified):
            return False
        # Иначе возвращает решение исполнителя
        return self.approved

    class Meta:
        unique_together = ['task', 'user']
        ordering = ['-price']


class File(m.Model):
    file = m.FileField()
    comment = m.CharField(blank=True, max_length=150)

    def get_task(self):
        task_file = getattr(self, 'task_file', None)
        if task_file:
            return task_file.task
        return getattr(self, 'comment_file', None).comment.task

    def get_owner(self):
        task_file = getattr(self, 'task_file', None)
        if task_file:
            return task_file.task.author
        return getattr(self, 'comment_file', None).comment.author

    def can_be_deleted(self):
        """
        Файл может быть удален
        1. Из заявки: если на неё не ответили
        2. Из комментария: если можно изменить комментарий
        """
        task_file = getattr(self, 'task_file', None)
        comment_file = getattr(self, 'comment_file', None)

        if task_file:
            if task_file.can_be_edited():
                return True
        # TODO тут падает ... не могу воспроизвести
        if comment_file.comment.can_be_edited():
            return True
        return False

class TaskFile(m.Model):
    task = m.ForeignKey(Task, related_name='files', on_delete=m.CASCADE)
    file = m.OneToOneField(File, on_delete=m.CASCADE, related_name='task_file')


@receiver(m.signals.pre_delete, sender=File)
def delete_file(sender, instance, *args, **kwargs):
    instance.file.delete(False)

@receiver(m.signals.pre_save, sender=Task)
def change_task(sender, instance: Task, *args, **kwargs):
    """
    Добавляет комментарий к измененному полю
    TODO нужен тест
    TODO Нужен список игнорируемых полей
    """
    if instance.id is not None:
        change_log = []
        previous = Task.objects.get(id=instance.id)
        checked_fields = [
            'name',
            'text',
            'wanted_deadline',
            'work_type',
            'work_direction',
        ]
        for field in checked_fields:
            previous_value = getattr(previous, field)
            current_value = getattr(instance, field)

            if previous_value != current_value:
                verbose_name = previous._meta.get_field(field).verbose_name
                change_log.append(
                    f'Поле "{verbose_name or field}" изменено из "{previous_value}" на "{current_value}".\n'
                )

        if change_log:
            instance.comments.create(
                author=instance.author,
                text=''.join(change_log)
            )
