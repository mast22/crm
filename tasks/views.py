from django.shortcuts import reverse, get_object_or_404, render
from common.const import PERFORMER_GROUP_NAME, MANAGER_GROUP_NAME
from django.db import models as m
from notifications.signals import notify
from django.views.generic import (
    DetailView,
    ListView,
    CreateView,
    UpdateView,
    DeleteView,
)
from .models import Task, TaskFile, File, TaskStatus
from .forms import CreateTaskForm, CreateTaskStatusForm, ChangeTaskForm, AddFileTaskForm
from django.http import HttpResponseRedirect
from django.contrib.postgres.search import SearchVector
from .const import TaskStatuses, TaskStatusTypes
from django.contrib.auth.mixins import PermissionRequiredMixin, UserPassesTestMixin
from django.http import Http404
from django.urls import reverse_lazy
from django.core.exceptions import PermissionDenied


class TaskDetail(UserPassesTestMixin, DetailView):
    model = Task

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['comments'] = self.object.comments.all()
        context['update_form'] = ChangeTaskForm(instance=self.get_object())
        user = self.request.user
        if user.is_performer():
            # Статусы этого пользователя
            context['task_statuses'] = self.object.task_statuses.filter(user=user).order_by('created')
            # Последний активный статус
            context['active_status'] = self.object.get_active_status(user)
        elif user.is_manager():
            # Статусы всех оценивших пользователей
            context['task_statuses'] = self.object.\
                task_statuses.\
                order_by('user', '-created').\
                distinct('user')
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


def change_task_view(request, pk):
    user = request.user
    if not user.is_manager():
        raise PermissionDenied

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
            queryset = queryset.exclude(
                m.Q(status__in=[TaskStatuses.IN_PROGRESS, TaskStatuses.COMPLETED]),
                ~m.Q(task_statuses__user=user)
            )

        return queryset


class AllTaskList(PermissionRequiredMixin, TaskTypeFilter, GroupFilterMixin, ListView):
    """Все заявки + фильтрация по поиску
    Игнорирует TaskListView
    """
    model = Task

    def get_queryset(self):
        query = self.request.GET.get('query')
        get_params = self.request.GET.get('work_types')
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
        elif get_params:
            try:
                ids = [int(param) for param in get_params.split(',')]
                queryset = queryset.filter(work_type_id__in=ids)
                print(ids)
            except:
                pass

        return queryset


class TaskStatusListView(PermissionRequiredMixin, TaskTypeFilter, GroupFilterMixin, ListView):
    """Представление с фильтрацией по статусу. Фильтрует только по статусу
    Игнорирует AllTaskList
    """
    model = Task

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


class CreateTaskView(UserPassesTestMixin, CreateView):
    form_class = CreateTaskForm
    # permission_required = 'tasks.add_task'
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

        return HttpResponseRedirect(reverse('tasks:task-list'))

    def test_func(self):
        return self.request.user.is_manager()


"""
TaskStatus
1. Создать - Создаётся TaskStatus
3. Изменить - Изменяется TaskStatus
4. Отказать - Создаётся TaskStatus с отказом
5. Принять из отказа
"""


def put_to_work(request, pk: int, status_id: int):
    user = request.user
    task = get_object_or_404(Task, pk=pk)

    if not (user.is_manager() or user == task.author):
        raise PermissionDenied

    task_status = get_object_or_404(TaskStatus, pk=status_id)

    task_status.type = TaskStatusTypes.IN_WORK
    task_status.save()
    task.status = TaskStatuses.IN_PROGRESS
    task.save()

    return HttpResponseRedirect(reverse('tasks:task-detail', args=(pk,)))


class FileUpdate(UserPassesTestMixin, UpdateView):
    model = File
    fields = ['comment']
    template_name_suffix = '_update_form'

    def get_success_url(self, **kwargs):
        # TODO тут много запросов
        try:
            reverse_url = reverse(
                'tasks:task-detail', kwargs={'pk': self.object.comment_file.comment.task.id}
            )
        except:
            reverse_url = reverse(
                'tasks:task-detail', kwargs={'pk': self.object.task_file.task.id }
            )
        return reverse_url

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


def add_files(request, task_id):
    task = get_object_or_404(Task, pk=task_id)
    if task.author == request.user:
        if request.method == 'POST':
            form = AddFileTaskForm(request.POST, request.FILES)
            if form.is_valid():
                task_files = []
                for file in request.FILES.getlist('files'):
                    task_files.append(TaskFile(task=task, file=File.objects.create(file=file)))
                TaskFile.objects.bulk_create(task_files)
                return HttpResponseRedirect(reverse('tasks:task-detail', args=(task_id,)))
            else:
                return render(request, template_name='tasks/task_add_files.html', context={'form': form})
        else:
            form = AddFileTaskForm()
            return render(request, template_name='tasks/task_add_files.html', context={'form': form})
    else:
        return PermissionDenied()


def delete_file(request, pk):
    file = get_object_or_404(File, pk=pk)
    owner = file.get_owner()
    if owner != request.user or not file.can_be_deleted():
        raise PermissionDenied
    task_id = file.get_task().id
    file.delete()

    return HttpResponseRedirect(reverse('tasks:task-detail', args=(task_id,)))


def check_actuality(request, pk: int):
    user = request.user
    task_status = get_object_or_404(TaskStatus, pk=pk)

    if user != task_status.task.author or not user.is_manager():
        raise PermissionDenied()

    task_status.approved = False
    task_status.save()

    notify.send(
        sender=request.user,
        recipient=task_status.user,
        verb='Ответил на комментарий',
        target=task_status.task,
        action_object=task_status,
    )

    return HttpResponseRedirect(reverse('tasks:task-detail', args=(task_status.task_id,)))


def accept_task(request, pk):
    user = request.user
    if user.is_manager():
        raise PermissionDenied

    task = get_object_or_404(Task, pk=pk)

    if request.method == 'POST':
        form = CreateTaskStatusForm(request.POST)
        if form.is_valid():
            TaskStatus.objects.create(
                task=task,
                user=user,
                type=TaskStatusTypes.ACCEPTED,
                price=form.cleaned_data['price'],
                deadline=form.cleaned_data['deadline'],
            )
            return HttpResponseRedirect(reverse('tasks:task-detail', args=(pk,)))
        return render(request, 'tasks/taskstatus_form.html', context={'form': form})
    else:
        form = CreateTaskStatusForm()
        return render(request, 'tasks/taskstatus_form.html', context={'form': form})

def reject_task(request, pk):
    user = request.user
    if user.is_manager():
        raise PermissionDenied
    task = get_object_or_404(Task, pk=pk)

    TaskStatus.objects.create(
        task=task,
        user=user,
        type=TaskStatusTypes.REJECTED,
    )
    return HttpResponseRedirect(reverse('tasks:task-detail', args=(pk,)))


def approve_status(request, pk):
    user = request.user
    if user.is_manager():
        raise PermissionDenied
    task = get_object_or_404(Task, pk=pk)
    task_status = task.get_active_status(user)

    task_status.approved = True
    task_status.save()

    return HttpResponseRedirect(reverse('tasks:task-detail', args=(pk,)))

def change_status(request, pk):
    """ На самом деле не изменяет, а создаёт новый. Просто старый становится не активным """
    user = request.user
    if user.is_manager():
        raise PermissionDenied

    task = get_object_or_404(Task, pk=pk)
    user = request.user

    active_status = task.get_active_status(user)
    if active_status:
        # Не обязательно, но мы проверяем если уже есть статусы
        # Их наличия обязательно для изменения статуса заявки
        if request.method == 'POST':
            form = CreateTaskStatusForm(request.POST)
            if form.is_valid():
                TaskStatus.objects.create(
                    task=task,
                    user=user,
                    type=TaskStatusTypes.ACCEPTED,
                    price=form.cleaned_data['price'],
                    deadline=form.cleaned_data['deadline'],
                )

            return HttpResponseRedirect(reverse('tasks:task-detail', args=(pk,)))
    else:
        return HttpResponseRedirect(reverse('tasks:task-detail', args=(pk,)))

    form = CreateTaskStatusForm(instance=task.get_active_status(user))
    return render(request, 'tasks/taskstatus_form.html', context={'form': form})