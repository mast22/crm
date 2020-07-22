from django.db import models as m
from mptt.models import MPTTModel, TreeForeignKey
from django.conf import settings
from tasks.models import Task, File


class Comment(MPTTModel):
    task = m.ForeignKey(Task, related_name='comments', on_delete=m.CASCADE)
    author = m.ForeignKey(settings.AUTH_USER_MODEL, on_delete=m.CASCADE)
    created_at = m.DateTimeField(auto_now_add=True)
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
    file = m.OneToOneField(File, on_delete=m.CASCADE, related_name='comment_file')
