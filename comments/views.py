from django.shortcuts import render, reverse, get_object_or_404
from django.views.generic import DetailView, ListView, CreateView, UpdateView
from .models import Task, Comment, File, CommentFile
from .forms import CreateCommentForm
from django.http import HttpResponseRedirect
from django.contrib.auth import get_user_model
from notifications.signals import notify


User = get_user_model()

class CommentDetail(DetailView):
    model = Comment
    context_object_name = 'comments'

    def get_object(self, queryset=None):
        """Включаем в queryset дочерние комменты"""
        obj = super(CommentDetail, self).get_object(queryset=queryset)
        return obj.get_descendants(include_self=True)



def comment_create(request, task_id, parent_id=None):
    if request.method == 'POST':
        form = CreateCommentForm(request.POST, request.FILES)
        if form.is_valid():
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
            files = []
            for f in request.FILES.getlist('files'):
                file = File.objects.create(file=f)
                files.append(CommentFile(comment=comment, file=file))
            CommentFile.objects.bulk_create(files)
            if parent:
                notify.send(sender=request.user, recipient=parent.author, verb='Ответил на комментарий', target=task, action_object=comment)
            return HttpResponseRedirect(reverse('tasks:task-detail', args=(task.id,)))
    else:
        form = CreateCommentForm()

    return render(request, 'comments/comment_form.html', context={'form': form})
