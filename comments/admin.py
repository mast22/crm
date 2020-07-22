from django.contrib import admin
from .models import Comment, CommentFile

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    pass


@admin.register(CommentFile)
class CommentFileAdmin(admin.ModelAdmin):
    pass
