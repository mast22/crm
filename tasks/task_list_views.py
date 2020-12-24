from django.views.generic import ListView
from django.db.models import Q
from .models import Task
from .const import TaskStatuses, TaskStatusTypes
from .filters import user_is_manager_filter, user_is_performer_filter, search_filter, left_bar_filter
from django.contrib.auth.mixins import PermissionRequiredMixin


class FilterArgs:
    incoming = 'incoming'
    in_process = 'in_process'
    new = 'new'
    questioned = 'questioned'
    rated = 'rated'
    assessment = 'assessment'
    rejected = 'rejected'


class TaskListView(ListView, PermissionRequiredMixin):
    model = Task
    template_name = 'tasks/task_list_2.html'

    def get_context_data(self, *, object_list=None, **kwargs):
        # Для каждой из роли мы должны передать также фильтры, которые мы должны отображать
        user = self.request.user
        context = super().get_context_data(**kwargs)
        filters = {}

        if user.is_manager():
            # Менеджер: Входящие, в работе
            filters['left_bar_filters'] = {
                FilterArgs.incoming: 'Входящие',
                FilterArgs.in_process: 'В работе'
            }
            # Менеджер: Новые, есть вопросы, оцененные
            filters['top_bar_filters'] = {
                FilterArgs.new: 'Новые',
                FilterArgs.questioned: 'Есть вопросы',
                FilterArgs.rated: 'Оцененные'
            }

        if user.is_performer():
            # Исполнитель: На оценке, в работе
            filters['left_bar_filters'] = {
                FilterArgs.assessment: 'На оценке',
                FilterArgs.in_process: 'В работе'
            }
            # Исполнитель: На оценке, отклоненные, оцененные
            filters['top_bar_filters'] = {
                FilterArgs.new: 'Новые',
                FilterArgs.rejected: 'Отклоненные',
                FilterArgs.rated: 'Оцененные'
            }

        context['filters'] = filters
        return context

    def get_queryset(self):
        queryset = super().get_queryset()
        user = self.request.user

        left_bar_param = self.request.GET.get('left-bar-filter', None)
        top_bar_param = self.request.GET.get('top-bar-filter', None)
        work_types_param = self.request.GET.get('work-types-filter', None)
        page_param = self.request.GET.get('page-param', None)
        search_param = self.request.GET.get('query', None)

        """
        Проведём начальную фильтрацию и не разделим доступ по группам
        """

        if user.is_manager():
            queryset = user_is_manager_filter(queryset, user)

        if user.is_performer():
            queryset = user_is_performer_filter(queryset, user)

        # Теперь наш список правильно отфильтрован и можно фильтровать по GET параметрам

        if work_types_param is not None:
            pass

        # В модифицированной версии не используем фильтрацию по параметрам left и top

        if left_bar_param is not None:
            # Менеджер: Входящие, в работе
            # Исполнитель: На оценке, в работе
            if user.is_manager():
                filters = {
                    FilterArgs.incoming: lambda qsf: qsf.filter(
                        Q(status=TaskStatuses.NEW) |
                        Q(author_id=user.id, status=TaskStatuses.QUESTIONED) |
                        Q(author_id=user.id, status=TaskStatuses.RATED) |
                        Q(author_id=user.id, status=TaskStatuses.IN_PROGRESS)
                    ),
                    FilterArgs.in_process: lambda qsf: qsf.filter(author_id=user.id, status=TaskStatuses.IN_PROGRESS)
                }

            if user.is_performer():
                filters = {
                    FilterArgs.in_process: lambda qsf: qsf.filter(
                        task_statuses__user=user, task_statuses__type=TaskStatusTypes.IN_WORK
                    ),
                    FilterArgs.assessment: lambda qsf: qsf.filter(
                        Q(status__in=[TaskStatuses.RATED, TaskStatuses.QUESTIONED]) |
                        Q(task_statuses__user=user, task_statuses__type=TaskStatusTypes.ACCEPTED) |
                        Q(task_statuses__user=user, task_statuses__type=TaskStatusTypes.REJECTED) |
                        Q(task_statuses__user=user, task_statuses__type=TaskStatusTypes.IN_WORK)
                    ),
                }
            filter = filters.get(left_bar_param, None)
            if filter:
                queryset = filter(queryset)


        if top_bar_param is not None:
            # Исполнитель: На оценке, отклоненные, оцененные
            # Менеджер: Новые, есть вопросы, оцененные
            if user.is_manager():
                filters = {
                    FilterArgs.new: lambda qsf: qsf.filter(status=TaskStatuses.NEW),
                    FilterArgs.questioned: lambda qsf: qsf.filter(author_id=user.id, status=TaskStatuses.QUESTIONED),
                    FilterArgs.rated: lambda qsf: qsf.filter(author_id=user.id, status=TaskStatuses.RATED),
                }

            if user.is_performer():
                filters = {
                    FilterArgs.new: lambda qsf: qsf.filter(
                        status=TaskStatuses.NEW
                    ),
                    FilterArgs.rated: lambda qsf: qsf.filter(
                        task_statuses__user=user, task_statuses__type=TaskStatusTypes.ACCEPTED
                    ),
                    FilterArgs.rejected: lambda qsf: qsf.filter(
                        task_statuses__user=user, task_statuses__type=TaskStatusTypes.REJECTED
                    ),
                }

            filter = filters.get(top_bar_param, None)
            if filter:
                queryset = filter(queryset)

        if search_param is not None:
            queryset = search_filter(queryset, search_param)

        if page_param is not None:
            pass

        return queryset