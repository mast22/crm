from django.db import models as m
from django.urls import reverse
from django.dispatch import receiver
from django.conf import settings
from .const import TaskStatuses, TASK_STATUS_CHOICES, WORK_TYPE_CHOICES


class File(m.Model):
    file = m.FileField()
    comment = m.CharField(blank=True, max_length=150)


class Task(m.Model):
    name = m.CharField('Название', max_length=150)
    text = m.TextField('Требования')
    author = m.ForeignKey(settings.AUTH_USER_MODEL, on_delete=m.CASCADE)
    created_at = m.DateTimeField(auto_now_add=True)
    status = m.CharField(
        'Статус', choices=TASK_STATUS_CHOICES, default=TaskStatuses.NEW, max_length=11
    )
    price = m.DecimalField(decimal_places=2, max_digits=10, null=True)
    wanted_deadline = m.DateField('Желаемый срок', null=True)
    deadline = m.DateField(null=True)
    phone = m.CharField('Номер телефона', max_length=150)
    whats_app = m.CharField('What\'s App', max_length=150)
    work_type = m.CharField('Тип работы', choices=WORK_TYPE_CHOICES, max_length=10)
    email = m.EmailField('Электронная почта')
    address = m.CharField('Адрес', max_length=150)
    company = m.CharField('Компания', max_length=150)


    class Meta:
        ordering = ['-created_at']

    def get_absolute_url(self):
        return reverse('task-detail', kwargs={'pk': self.pk})


class TaskFile(m.Model):
    task = m.ForeignKey(Task, related_name='files', on_delete=m.CASCADE)
    file = m.OneToOneField(File, on_delete=m.CASCADE, related_name='task_file')


@receiver(m.signals.pre_delete, sender=File)
def delete_file(sender, instance, *args, **kwargs):
    instance.file.delete(False)
