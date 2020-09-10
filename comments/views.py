from django.shortcuts import render, reverse, get_object_or_404
from django.views.generic import DetailView, ListView, CreateView, UpdateView
from .models import Task, Comment, File, CommentFile
from .forms import CreateCommentForm, AddFileForm
from django.http import HttpResponseRedirect
from django.contrib.auth import get_user_model
from notifications.signals import notify
from tasks.const import TaskStatuses
from common.const import PERFORMER_GROUP_NAME, MANAGER_GROUP_NAME
from django.core.exceptions import PermissionDenied

User = get_user_model()


class CommentDetail(DetailView):
    model = Comment
    context_object_name = 'comments'

    def get_object(self, queryset=None):
        """Включаем в queryset дочерние комменты"""
        obj = super(CommentDetail, self).get_object(queryset=queryset)
        return obj.get_descendants(include_self=True)

def delete_comment(request, pk):
    comment = get_object_or_404(Comment, pk=pk)

    if comment.can_be_edited() and request.user == comment.author:
        comment.delete()

    return HttpResponseRedirect(reverse('tasks:task-detail', args=(comment.task_id,)))


def comment_create(request, task_id, parent_id=None):
    if request.method == 'POST':
        form = CreateCommentForm(request.POST, request.FILES)
        if form.is_valid():
            user = request.user
            if parent_id is not None:
                parent = Comment.objects.filter(id=parent_id).first()
            else:
                parent = None
            task = get_object_or_404(Task, id=task_id)

            comment = Comment.objects.create(
                task=task,
                parent=parent,
                author=request.user,
                text=form.cleaned_data['text'],
            )

            # Логика изменения статуса

            if (
                task.status == TaskStatuses.NEW
                and user.groups.filter(name=PERFORMER_GROUP_NAME).exists()
            ):
                # Если статус заявки новый и исполнитель пишет комментарий
                # То статус меняется на "есть вопросы"
                task.status = TaskStatuses.QUESTIONED
                task.save()

            if (
                task.status == TaskStatuses.QUESTIONED
                and user.groups.filter(name=MANAGER_GROUP_NAME).exists()
            ):
                # Если статус заявки "есть вопросы" и менеджер пишет комментарий
                # То статус меняется на "На оценке"
                task.status = TaskStatuses.NEW
                task.save()

            files = []
            for f in request.FILES.getlist('files'):
                file = File.objects.create(file=f)
                files.append(CommentFile(comment=comment, file=file))
            CommentFile.objects.bulk_create(files)
            if parent:
                notify.send(
                    sender=user,
                    recipient=parent.author,
                    verb='Ответил на комментарий',
                    target=task,
                    action_object=comment,
                )
            return HttpResponseRedirect(reverse('tasks:task-detail', args=(task.id,)))
    else:
        form = CreateCommentForm()

    return render(request, 'comments/comment_form.html', context={'form': form})


class CommentUpdate(UpdateView):
    model = Comment
    fields = ['text']

    def get_success_url(self):
        comment = self.get_object()
        return reverse('tasks:task-detail', args=(comment.task_id,))

def add_files(request, pk):
    comment = get_object_or_404(Comment, pk=pk)
    if comment.author == request.user:
        if request.method == 'POST':
            form = AddFileForm(request.POST, request.FILES)
            if form.is_valid():
                comment_files = []
                for file in request.FILES.getlist('files'):
                    file_instance = File.objects.create(file=file)
                    comment_files.append(CommentFile(comment=comment, file=file_instance))
                CommentFile.objects.bulk_create(comment_files)
                return HttpResponseRedirect(reverse('tasks:task-detail', args=(comment.task_id,)))
            else:
                return render(request, template_name='comments/comment_add_files.html', context={'form': form})
        else:
            form = AddFileForm()
            return render(request, template_name='comments/comment_add_files.html', context={'form': form})
    else:
        return PermissionDenied()