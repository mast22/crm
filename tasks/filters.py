from .models import Task
from django_filters import FilterSet, Filter, NumberFilter


class WorkTypeFilter(FilterSet):
    # work_types = NumberFilter(field_name='work_type', lookup_expr='in')

    class Meta:
        model = Task
        fields = ['work_type_id']