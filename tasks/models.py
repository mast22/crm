from django.db import models as m
from mptt.models import MPTTModel, TreeForeignKey
from django.dispatch import receiver
from django.conf import settings
from .const import TaskStatuses, TASK_STATUS_CHOICES


class File(m.Model):
    file = m.FileField()


class Task(m.Model):
    name = m.CharField('Название', max_length=150)
    text = m.TextField('Требования')
    author = m.ForeignKey(settings.AUTH_USER_MODEL, on_delete=m.CASCADE)
    created_at = m.DateTimeField(auto_now_add=True)
    status = m.CharField(
        'Статус', choices=TASK_STATUS_CHOICES, default=TaskStatuses.NEW, max_length=11
    )

    class Meta:
        ordering = ['-created_at']


class TaskFile(m.Model):
    task = m.ForeignKey(Task, related_name='files', on_delete=m.CASCADE)
    file = m.OneToOneField(File, on_delete=m.CASCADE)


class Comment(MPTTModel):
    task = m.ForeignKey(Task, related_name='comments', on_delete=m.CASCADE)
    author = m.ForeignKey(settings.AUTH_USER_MODEL, on_delete=m.CASCADE)
    date_time = m.DateTimeField(auto_now_add=True)
    text = m.TextField('Текст')
    parent = TreeForeignKey(
        'self',
        related_name='children',
        null=True,
        blank=True,
        db_index=True,
        on_delete=m.CASCADE,
    )

    def __str__(self):
        return f'{self.author}-{self.task}'


class CommentFile(m.Model):
    comment = m.ForeignKey(Comment, related_name='files', on_delete=m.CASCADE)
    file = m.OneToOneField(File, on_delete=m.CASCADE)


@receiver(m.signals.pre_delete, sender=File)
def delete_file(sender, instance, *args, **kwargs):
    instance.file.delete(False)
