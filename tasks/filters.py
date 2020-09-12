from .models import Task, WorkType
import django_filters


class TaskFilter(django_filters.FilterSet):
    work_types = django_filters.ModelMultipleChoiceFilter(
        queryset = WorkType.objects.all(),
        field_name='work_type_id',
    )

    class Meta:
        model = Task
        fields = ['work_types']