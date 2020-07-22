from django.shortcuts import render, reverse, get_object_or_404
from django.views.generic import DetailView, ListView, CreateView, UpdateView
from .models import Task, TaskFile, File
from .forms import CreateTaskForm
from django.http import HttpResponseRedirect
from .tasks import reply_email
from django.contrib.auth import get_user_model
from django.contrib.postgres.search import SearchVector
from .const import TaskStatuses
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

    def get_queryset(self):
        query = self.request.GET.get('query')
        if query.startswith('#'):
            return Task.objects.annotate(search=SearchVector('id')).filter(search=query[1:])
        else:
            return Task.objects.annotate(search=SearchVector('name', 'text')).filter(search=query)


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





class TaskUpdate(UpdateView):
    model = Task
    fields = ['price', 'deadline']
    template_name_suffix = '_update_form'

    def form_valid(self, form):
        obj = form.save(commit=False)
        obj.status = TaskStatuses.RATED
        obj.save()

        return HttpResponseRedirect(reverse('tasks:task-detail', args=(obj.id,)))

class FileUpdate(UpdateView):
    model = File
    fields = ['comment']
    template_name_suffix = '_update_form'

    def get_success_url(self, **kwargs):
        # TODO тут много запросов
        return reverse('tasks:task-detail', kwargs={'pk': self.object.comment_file.comment.task.id})

