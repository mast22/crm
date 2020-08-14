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

    def can_be_edited(self):
        """
        Комментарий может быть изменён
        Комментарий не может быть изменён если:
        1. В заявке уже ответила другая сторона
        2. Это комментарий пользователя
        """
        return not bool(Comment.objects.filter(
            m.Q(task=self.task, created_at__gte=self.created_at) &
            ~m.Q(author__groups=self.author.groups.first())
        ).first())


class CommentFile(m.Model):
    comment = m.ForeignKey(Comment, related_name='files', on_delete=m.CASCADE)
    file = m.OneToOneField(File, on_delete=m.CASCADE, related_name='comment_file')
