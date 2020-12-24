from django.db.models import QuerySet
from users.models import User
from .const import TaskStatuses
from django.db import models as m
from django.http import HttpResponseBadRequest
from django.contrib.postgres.search import SearchVector


def user_is_manager_filter(queryset: QuerySet, user: User) -> QuerySet:
    return queryset.filter(author=user)


def user_is_performer_filter(queryset: QuerySet, user: User) -> QuerySet:
    """
    Для исполнителя удаляем заявки, которые находятся в прогрессе у других ТЛов
    И которые были завершены не текущим пользователем
    """
    queryset = queryset.exclude(
        m.Q(status__in=[TaskStatuses.IN_PROGRESS, TaskStatuses.COMPLETED]),
        ~m.Q(task_statuses__user=user)
    )

    """
    Также для исполнителя фильтруем по заданым ему типа работ
    """

    queries = {}
    work_types = user.work_types.all()
    work_directions = user.work_directions.all()

    if work_types:
        queries['work_type__in'] = work_types
    if work_directions:
        queries['work_direction__in'] = work_directions
    return queryset.filter(**queries)


def left_bar_filter(queryset: QuerySet, data: str) -> QuerySet:
    pass


def search_filter(queryset: QuerySet, data: str) -> QuerySet:
    if data.startswith('#'):
        number = data[1:]
        try:
            task_id = int(number)
        except ValueError as e:
            raise HttpResponseBadRequest
        queryset = queryset.annotate(search=SearchVector('id')).filter(
            search=str(task_id)
        )
    else:
        queryset = queryset.annotate(
            search=SearchVector('name', 'text')
        ).filter(search=data)

    return queryset

