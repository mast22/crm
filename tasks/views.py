from django.shortcuts import reverse, get_object_or_404, render
from django.views.generic import (
    DetailView,
    ListView,
    CreateView,
    UpdateView,
    DeleteView,
)
from .models import Task, TaskFile, File, TaskStatus
from .forms import CreateTaskForm, RateTaskForm
from django.http import HttpResponseRedirect
from users.models import User
from django.contrib.postgres.search import SearchVector
from .const import TaskStatuses
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.http import Http404
from django.contrib.auth.decorators import user_passes_test
from django.urls import reverse_lazy


class TaskDetail(PermissionRequiredMixin, DetailView):
    model = Task
    permission_required = 'tasks.view_task'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['comments'] = Task.objects.get(pk=self.kwargs['pk']).comments.all()
        return context


class AllTaskList(PermissionRequiredMixin, ListView):
    model = Task
    permission_required = 'tasks.view_task'

    def get_queryset(self):
        query = self.request.GET.get('query')
        if query:
            if query.startswith('#'):
                return Task.objects.annotate(search=SearchVector('id')).filter(
                    search=query[1:]
                )
            else:
                return Task.objects.annotate(
                    search=SearchVector('name', 'text')
                ).filter(search=query)
        return Task.objects.all()


class FilterByStatusTaskView(PermissionRequiredMixin, ListView):
    model = Task
    permission_required = 'tasks.view_task'

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


class CreateTaskView(PermissionRequiredMixin, CreateView):
    form_class = CreateTaskForm
    permission_required = 'tasks.add_task'
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


def accept_task(request, pk):
    if request.method == 'POST':
        form = RateTaskForm(request.POST)
        if form.is_valid():
            TaskStatus.objects.create(
                task_id=pk,
                user=request.user,
                price=form.cleaned_data['price'],
                deadline=form.cleaned_data['deadline'],
            )
    else:
        form = RateTaskForm()
        return render(request, 'tasks/task_accept.html', context={'form': form})

    return HttpResponseRedirect(reverse('tasks:task-detail', args=(pk,)))


@user_passes_test(User.is_team_leader)
def reject_task(request, pk):
    task = get_object_or_404(Task, pk=pk)
    task.status = TaskStatuses.REJECTED
    task.save()

    return HttpResponseRedirect(reverse('tasks:task-list', args=(task.id,)))


class FileUpdate(UpdateView):
    model = File
    fields = ['comment']
    template_name_suffix = '_update_form'

    def get_success_url(self, **kwargs):
        # TODO тут много запросов
        return reverse(
            'tasks:task-detail', kwargs={'pk': self.object.comment_file.comment.task.id}
        )


class DeleteTaskView(DeleteView):
    model = Task
    success_url = reverse_lazy('tasks:task-list')
