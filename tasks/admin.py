from django.contrib import admin
from .models import Task, Comment, TaskFile, CommentFile, File

# Register your models here.


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    pass


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    pass


@admin.register(TaskFile)
class TaskFileAdmin(admin.ModelAdmin):
    pass


@admin.register(CommentFile)
class CommentFileAdmin(admin.ModelAdmin):
    pass


@admin.register(File)
class FileAdmin(admin.ModelAdmin):
    pass