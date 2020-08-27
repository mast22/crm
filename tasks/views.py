from django.shortcuts import reverse, get_object_or_404, render
from common.const import PERFORMER_GROUP_NAME, MANAGER_GROUP_NAME
from django.db import models as m
from django.views.generic import (
    DetailView,
    ListView,
    CreateView,
    UpdateView,
    DeleteView,
)
from .models import Task, TaskFile, File, TaskStatus
from .forms import CreateTaskForm, RateTaskForm, ChangeTaskForm
from django.http import HttpResponseRedirect
from django.contrib.postgres.search import SearchVector
from .const import TaskStatuses, TaskStatusTypes
from django.contrib.auth.mixins import PermissionRequiredMixin, UserPassesTestMixin
from django.http import Http404
from django.urls import reverse_lazy
from django.contrib import messages
from django.contrib.auth.decorators import permission_required
from django.core.exceptions import PermissionDenied


class TaskDetail(PermissionRequiredMixin, UserPassesTestMixin, DetailView):
    model = Task
    permission_required = 'tasks.view_task'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['comments'] = self.object.comments.all()
        context['update_form'] = ChangeTaskForm(instance=self.get_object())
        user = self.request.user
        context['task_status'] = None
        if user.has_perm('tasks.can_rate_task'):
            context['task_status'] = self.object.task_statuses.filter(user=user).first()
        return context

    def test_func(self):
        """ПМ могут смотреть только свои заявки"""
        user = self.request.user
        if user.is_superuser:
            return True
        if (
            self.request.user.has_perm('tasks.can_put_to_work')
            and self.get_object().author != self.request.user
        ):
            return False
        return True


@permission_required('tasks.can_see_extra')
def change_task_view(request, pk):
    if request.method == 'POST':
        form = ChangeTaskForm(request.POST, instance=get_object_or_404(Task, pk=pk))
        form.save()

    return HttpResponseRedirect(reverse('tasks:task-detail', args=(pk,)))


class TaskTypeFilter:
    def get_queryset(self):
        user = self.request.user
        qs = super().get_queryset()

        if user.is_performer():
            queries = {}
            work_types = user.work_types.all()
            work_directions = user.work_directions.all()

            if work_types:
                queries['work_type__in'] = work_types
            if work_directions:
                queries['work_direction__in'] = work_directions
            qs = qs.filter(**queries)

        return qs


class GroupFilterMixin:
    def get_queryset(self):
        queryset = super().get_queryset()
        user = self.request.user
        if user.is_manager():
            queryset = queryset.filter(author=user)

        if user.is_performer():
            """
            Для исполнителя удаляем заявки, которые находятся в прогрессе у других ТЛов
            И которые были завершены не текущим пользователем
            """
            queryset = queryset.filter(
                ~m.Q(status__in=[TaskStatuses.IN_PROGRESS, TaskStatuses.COMPLETED],)
                & ~m.Q(task_statuses__user=user))

        return queryset


class AllTaskList(PermissionRequiredMixin, TaskTypeFilter, GroupFilterMixin, ListView):
    model = Task
    permission_required = 'tasks.view_task'

    def get_queryset(self):
        query = self.request.GET.get('query')
        queryset = super().get_queryset()
        if query:
            if query.startswith('#'):
                queryset = queryset.annotate(search=SearchVector('id')).filter(
                    search=query[1:]
                )
            else:
                queryset = queryset.annotate(
                    search=SearchVector('name', 'text')
                ).filter(search=query)
            return queryset
        else:
            return queryset


class TaskListView(PermissionRequiredMixin, TaskTypeFilter, GroupFilterMixin, ListView):
    model = Task
    permission_required = 'tasks.view_task'

    def get_queryset(self):
        modifier = self.kwargs['modifier']
        user = self.request.user
        # Запретим доступы для групп
        if modifier.startswith('performer') and not user.groups.filter(name=PERFORMER_GROUP_NAME):
            raise PermissionDenied()
        if modifier.startswith('manager') and not user.groups.filter(name=MANAGER_GROUP_NAME):
            raise PermissionDenied()

        qs = super().get_queryset()

        # В другом миксине мы уже фильтруем по группам
        filters = {
            # Копипаста из лямбд ниже, лучше придумать как переделать
            'manager-incoming': lambda qsf: qsf.filter(
                m.Q(status=TaskStatuses.NEW) |
                m.Q(author_id=user.id, status=TaskStatuses.QUESTIONED) |
                m.Q(author_id=user.id, status=TaskStatuses.RATED) |
                m.Q(author_id=user.id, status=TaskStatuses.IN_PROGRESS)
            ),
            'manager-new': lambda qsf: qsf.filter(status=TaskStatuses.NEW),
            'manager-questioned': lambda qsf: qsf.filter(author_id=user.id, status=TaskStatuses.QUESTIONED),
            'manager-rated': lambda qsf: qsf.filter(author_id=user.id, status=TaskStatuses.RATED),
            'manager-in-process': lambda qsf: qsf.filter(author_id=user.id, status=TaskStatuses.IN_PROGRESS),

            # Копипаста из лямбд ниже, лучше придумать как переделать
            'performer-incoming': lambda qsf: qsf.filter(
                m.Q(status__in=[TaskStatuses.NEW, TaskStatuses.RATED, TaskStatuses.QUESTIONED]) |
                m.Q(task_statuses__user=user, task_statuses__type=TaskStatusTypes.ACCEPTED) |
                m.Q(task_statuses__user=user, task_statuses__type=TaskStatusTypes.REJECTED) |
                m.Q(task_statuses__user=user, task_statuses__type=TaskStatusTypes.IN_WORK)
            ),
            'performer-new': lambda qsf: qsf.filter(status__in=[TaskStatuses.NEW, TaskStatuses.RATED, TaskStatuses.QUESTIONED]),
            'performer-rated': lambda qsf: qsf.filter(task_statuses__user=user, task_statuses__type=TaskStatusTypes.ACCEPTED),
            'performer-rejected': lambda qsf: qsf.filter(task_statuses__user=user, task_statuses__type=TaskStatusTypes.REJECTED),
            'performer-in-process': lambda qsf: qsf.filter(task_statuses__user=user, task_statuses__type=TaskStatusTypes.IN_WORK),
        }

        # Объединяет первые 3 фильтра исполнителя
        # filters['performer-incoming'] = lambda qs: qs.filters['performer-new'].filters['performer-rated'].filters['performer-rejected']
        # Объединяет первые 3 фильтра менеджера
        # filters['manager-incoming'] = lambda qs: qs.filters['manager-new'].filters['manager-questioned'](qs).filters['manager-in-process'](qs)
        if modifier in filters.keys():
            filter = filters[modifier]
            qs = filter(qs)
        else:
            raise Http404
        return qs


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
5. Принять из отказа
"""


@permission_required('tasks.can_rate_task')
def accept_task_status(request, pk):
    task = get_object_or_404(Task, pk=pk)

    if request.method == 'POST':
        task_status = TaskStatus.objects.filter(user=request.user, task=task, ).first()
        if task_status:
            messages.info(request, 'Уже оценена')
            return HttpResponseRedirect(reverse('tasks:task-detail', args=(pk,)))

        form = RateTaskForm(request.POST)

        if form.is_valid():
            task_status = form.save(commit=False)
            task_status.task = task
            task_status.user = request.user
            task_status.save()
            return HttpResponseRedirect(reverse('tasks:task-detail', args=(pk,)))

    form = RateTaskForm()
    return render(request, 'tasks/taskstatus_form.html', context={'form': form})


@permission_required('can_rate_task')
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

    return render(request, reverse('tasks:task-detail', args=(task_id,)), status=200)


@permission_required('tasks.can_put_to_work')
def put_to_work(request, pk):
    task = get_object_or_404(Task, pk=pk)

    if request.user != task.author:
        raise PermissionDenied()

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
    task.prepayment_received = True
    task.save()

    return HttpResponseRedirect(reverse('tasks:task-detail', args=(pk,)))


@permission_required('tasks.can_put_to_work')
def accept_from_rejected(request, pk):
    task = get_object_or_404(Task, pk=pk)
    task_status = TaskStatus.objects.filter(task_id=pk, type=TaskStatusTypes.REJECTED).first()

    if task.status == TaskStatuses.IN_PROGRESS:
        messages.info(request, 'Заявка уже в работе, изменения не принимаются')
        return HttpResponseRedirect(reverse('tasks:task-detail', args=(pk,)))

    if task_status is None:
        messages.info(request, 'Заявка ещё не была отклонена')
        return HttpResponseRedirect(reverse('tasks:task-detail', args=(pk,)))

    if task_status.type == TaskStatusTypes.ACCEPTED:
        messages.info(request, 'Заявка уже принята')
        return HttpResponseRedirect(reverse('tasks:task-detail', args=(pk,)))

    if request.method == 'POST':
        form = RateTaskForm(request.POST, instance=task_status)

        if form.is_valid():
            task_status = form.save(commit=False)
            task_status.type = TaskStatusTypes.ACCEPTED
            task_status.user = request.user
            task_status.task = task
            task_status.save()

        else:
            return render(request, template_name='tasks/taskstatus_form.html', context={'form': form})

        return HttpResponseRedirect(reverse('tasks:task-detail', args=(pk,)))

    return render(request, template_name='tasks/taskstatus_form.html', context={'form': RateTaskForm()})


@permission_required('tasks.can_rate_task')
def change_task_status(request, pk):
    task_status = TaskStatus.objects.filter(task_id=pk, user=request.user).first()
    if task_status:
        if task_status.task.status == TaskStatuses.IN_PROGRESS:
            messages.info(request, 'Заявка в работе. Её нельзя изменить')
            return HttpResponseRedirect(reverse('tasks:task-detail', args=(pk,)))

        if request.method == 'POST':

            form = RateTaskForm(request.POST, instance=task_status)

            if form.is_valid():
                form.save()

            else:
                return render(request, 'tasks/change_task_status.html', context={'form': form})

            return HttpResponseRedirect(reverse('tasks:task-detail', args=(pk,)))

        form = RateTaskForm(instance=task_status)
        return render(request, 'tasks/change_task_status.html', context={'form': form})

    messages.info(request, 'Оценка не была создана')
    return HttpResponseRedirect(reverse('tasks:task-detail', args=(pk,)))


class FileUpdate(UserPassesTestMixin, UpdateView):
    model = File
    fields = ['comment']
    template_name_suffix = '_update_form'

    def get_success_url(self, **kwargs):
        # TODO тут много запросов
        return reverse(
            'tasks:task-detail', kwargs={'pk': self.object.comment_file.comment.task.id}
        )

    def test_func(self):
        task_file = getattr(self.get_object(), 'task_file', None)
        comment_file = getattr(self.get_object(), 'comment_file', None)

        if task_file:
            if task_file.task.author == self.request.user:
                return True
        # TODO тут падает
        if comment_file.comment.author == self.request.user:
            return True
        return False


class DeleteTaskView(UserPassesTestMixin, DeleteView):
    model = Task
    success_url = reverse_lazy('tasks:task-list')

    def test_func(self):
        return self.get_object().author == self.request.user


def add_files(request, pk, target):
    print(pk, target)
    return HttpResponseRedirect(reverse('tasks:task-list'))


def delete_file(request, pk):
    file = get_object_or_404(File, pk=pk)
    owner = file.get_owner()
    if owner != request.user or not file.can_be_deleted():
        raise PermissionDenied
    task_id = file.get_task().id
    file.delete()

    return HttpResponseRedirect(reverse('tasks:task-detail', args=(task_id,)))
