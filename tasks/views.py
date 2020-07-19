from django.shortcuts import render, reverse
from django.views.generic import DetailView, ListView, CreateView
from .models import Task, Comment, TaskFile, File, CommentFile
from .forms import CreateCommentForm, CreateTaskForm
from django.http import HttpResponseRedirect
from .tasks import reply_email
from django.contrib.auth import get_user_model
from .const import TASK_STATUS_CHOICES, TaskStatuses
from django.http import Http404

User = get_user_model()


class TaskDetail(DetailView):
    model = Task

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['comments'] = Task.objects.get(pk=self.kwargs['pk']).comments.all()
        return context


class AllTaskList(ListView):
    model = Task


class FilterByStatusTaskView(ListView):
    model = Task

    def get_queryset(self):
        status = self.kwargs['status']
        incoming_statuses = [
            TaskStatuses.NEW,
            TaskStatuses.RATED,
            TaskStatuses.REJECTED,
        ]
        if status == 'incoming':
            return Task.objects.filter(status__in=incoming_statuses)
        elif status in incoming_statuses:
            return Task.objects.filter(status=status)
        elif status == TaskStatuses.IN_PROGRESS:
            return Task.objects.filter(status=TaskStatuses.IN_PROGRESS)
        else:
            return Http404()


class CreateTaskView(CreateView):
    form_class = CreateTaskForm
    model = Task

    def form_valid(self, form):
        obj = form.save(commit=False)
        obj.author = self.request.user
        obj.save()

        files = []
        if self.request.FILES:
            for f in self.request.FILES.getlist('files'):
                file = File.objects.create(file=f)
                files.append(TaskFile(task=obj, file=file))

        TaskFile.objects.bulk_create(files)

        return HttpResponseRedirect(reverse('tasks:task-detail', args=(obj.id,)))


class CommentDetail(DetailView):
    model = Comment
    context_object_name = 'comments'

    def get_object(self, queryset=None):
        """Включаем в queryset дочерние комменты"""
        obj = super(CommentDetail, self).get_object(queryset=queryset)
        return obj.get_descendants(include_self=True)


def comment_create(request, task, parent=None):
    if request.method == 'POST':
        form = CreateCommentForm(request.POST, request.FILES)
        if form.is_valid():
            comment = Comment.objects.create(
                task_id=task,
                parent_id=parent,
                author=request.user,
                text=form.cleaned_data['text'],
            )
            files = []
            for f in request.FILES.getlist('files'):
                file = File.objects.create(file=f)
                files.append(CommentFile(comment=comment, file=file))
            CommentFile.objects.bulk_create(files)
            if parent:
                reply_email(Comment.objects.get(pk=parent).author, comment)
            return HttpResponseRedirect(reverse('tasks:task-detail', args=(task,)))
    else:
        form = CreateCommentForm()

    return render(request, 'tasks/comment_form.html', context={'form': form})
