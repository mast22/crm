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
from .const import TaskStatuses, TaskStatusTypes
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.http import Http404
from django.urls import reverse_lazy
from django.contrib import messages


class TaskDetail(PermissionRequiredMixin, DetailView):
    model = Task
    permission_required = 'tasks.view_task'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['comments'] = self.object.comments.all()
        user = self.request.user
        context['task_status'] = None
        if user.has_perm('tasks.can_rate_task'):
            context['task_status'] = self.object.task_statuses.filter(user=user).first()
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


"""
TaskStatus
1. Создать - Создаётся TaskStatus
3. Изменить - Изменяется TaskStatus
4. Отказать - Создаётся TaskStatus с отказом
"""


class AcceptTaskStatusView(CreateView):
    form_class = RateTaskForm
    permission_required = 'tasks.can_rate_task'
    model = TaskStatus


def reject_task(request, task_id):
    # Проверяем если мы уже приняли заявку
    user = request.user
    task_status = TaskStatus.objects.filter(task=task_id, user=user).first()
    if task_status:
        task_status.deadline = None
        task_status.price = None
        task_status.type = TaskStatusTypes.REJECTED
        task_status.save()

        return HttpResponseRedirect(reverse('tasks:task-detail', args=(task_id,)))

    # Если его нет, то создаём
    TaskStatus.objects.create(task_id=task_id, user=user, type=TaskStatusTypes.REJECTED)

    return HttpResponseRedirect(reverse('tasks:task-detail', args=(task_id,)))


def put_to_work(request, pk):
    task = get_object_or_404(Task, pk=pk)
    task_status = (
        task.task_statuses.filter(type=TaskStatusTypes.ACCEPTED)
        .order_by('-price')
        .first()
    )
    if task_status:
        task_status.type = TaskStatusTypes.IN_WORK
        task_status.save()
    else:
        messages.add_message(
            request,
            messages.ERROR,
            'Никто из исполнителей ещё не принял заявку',
            extra_tags='danger',
        )
        return HttpResponseRedirect(reverse('tasks:task-detail', args=(pk,)))

    task.status = TaskStatuses.IN_PROGRESS
    task.save()

    return HttpResponseRedirect(reverse('tasks:task-detail', args=(pk,)))


class ChangeTaskStatusView(UpdateView):
    model = TaskStatus
    fields = ['deadline', 'price']
    template_name = 'tasks/change_task_status.html'

    def get_success_url(self, **kwargs):
        # TODO тут много запросов
        return reverse('tasks:task-detail', kwargs={'pk': self.object.task_id})


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
