from django.shortcuts import render, reverse
from django.views.generic import DetailView, ListView, CreateView
from .models import Task, Comment, TaskFiles
from .forms import CreateCommentForm, CreateTaskForm
from django.http import HttpResponseRedirect
from .tasks import reply_email
from django.contrib.auth import get_user_model

User = get_user_model()


class TaskDetail(DetailView):
    model = Task

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['comments'] = Task.objects.get(pk=self.kwargs['pk']).comments.all()
        return context


class TaskList(ListView):
    model = Task


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
                files.append(TaskFiles(task=obj, file=f))

        TaskFiles.objects.bulk_create(files)

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
        form = CreateCommentForm(request.POST)
        if form.is_valid():
            comment = Comment.objects.create(
                task_id=task,
                parent_id=parent,
                author=request.user,
                text=form.cleaned_data['text'],
            )
            if parent:
                reply_email(Comment.objects.get(pk=parent).author, comment)
            return HttpResponseRedirect(reverse('tasks:task-detail', args=(task,)))
    else:
        form = CreateCommentForm()

    return render(request, 'tasks/comment_form.html', context={'form': form})
