from django.db import models as m
from django.urls import reverse
from django.dispatch import receiver
from django.conf import settings
from .const import (
    TaskStatuses,
    TASK_STATUS_CHOICES,
    WORK_TYPE_CHOICES,
    TASK_STATUS_TYPES_CHOICES,
    TaskStatusTypes,
)
from users.models import User


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
        # TODO тут падает
        if comment_file.comment.can_be_edited():
            return True
        return False


class Task(m.Model):
    name = m.CharField('Название', max_length=150)
    text = m.TextField('Требования')
    author = m.ForeignKey(settings.AUTH_USER_MODEL, on_delete=m.CASCADE)
    created_at = m.DateTimeField(auto_now_add=True)
    status = m.CharField(
        'Статус', choices=TASK_STATUS_CHOICES, default=TaskStatuses.NEW, max_length=11
    )
    customer_name = m.CharField('Имя клиента',max_length=150)
    wanted_deadline = m.DateField('Желаемый срок', null=True)
    phone = m.CharField('Номер телефона', max_length=150)
    whats_app = m.CharField('What\'s App', max_length=150)
    work_type = m.CharField('Тип работы', choices=WORK_TYPE_CHOICES, max_length=10)
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

    # def can_change_task_data(self, user: User) -> bool:
    #     """
    #     Данные заявки для пользователя могут быть изменены
    #     Если другая сторона ещё не ответила
    #     """
    #     return not bool(self.comments.filter(
    #         m.Q(task=self, created_at__gte=self.created_at) &
    #         ~m.Q(author__groups=user.groups.first())
    #     ).first())

    def can_be_edited(self):
        """
        Решаем если можно изменять заявку.
        Заявку нельзя изменять если:
        1. Она уже завершена или в прогрессе
        """
        return self.status in [TaskStatuses.COMPLETED, TaskStatuses.IN_PROGRESS]


class TaskStatus(m.Model):
    task = m.ForeignKey(Task, on_delete=m.CASCADE, related_name='task_statuses')
    user = m.ForeignKey(User, on_delete=m.CASCADE, related_name='task_statuses')
    last_modified = m.DateTimeField(auto_now=True)
    type = m.CharField(choices=TASK_STATUS_TYPES_CHOICES, max_length=8)
    price = m.DecimalField(decimal_places=2, max_digits=10, null=True)
    deadline = m.DateField(null=True)

    def is_rejected(self):
        return (
            self.type == TaskStatusTypes.REJECTED
            and self.deadline is None
            and self.price is None
        )

    class Meta:
        unique_together = ['task', 'user']
        ordering = ['-price']


class TaskFile(m.Model):
    task = m.ForeignKey(Task, related_name='files', on_delete=m.CASCADE)
    file = m.OneToOneField(File, on_delete=m.CASCADE, related_name='task_file')


@receiver(m.signals.pre_delete, sender=File)
def delete_file(sender, instance, *args, **kwargs):
    instance.file.delete(False)
