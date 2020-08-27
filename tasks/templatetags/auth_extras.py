from django import template
from django.contrib.auth.models import Group

register = template.Library()


@register.filter(name='has_group')
def has_group(user, group_name):
    belonger = Group.objects.filter(name=group_name, user=user).exists()
    return belonger


@register.filter(name='task_sequence')
def task_sequence(user_id: int, task_id: int):
    return user_id + task_id