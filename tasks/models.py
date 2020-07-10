from django.db import models as m
from mptt.models import MPTTModel, TreeForeignKey
from django.conf import settings


class Task(m.Model):
    name = m.CharField(max_length=150)
    text = m.TextField()
    author = m.ForeignKey(settings.AUTH_USER_MODEL, on_delete=m.CASCADE)
    created_at = m.DateTimeField(auto_now_add=True)


class TaskFiles(m.Model):
    task = m.ForeignKey(Task, related_name='files', on_delete=m.CASCADE)
    file = m.FileField()


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

