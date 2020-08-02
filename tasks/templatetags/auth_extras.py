from django import template
from django.contrib.auth.models import Group

register = template.Library()


@register.filter(name='has_group')
def has_group(user, group_name):
    belonger = Group.objects.filter(name=group_name, user=user).exists()
    return belonger

# @register.filter(name='resolve_status')
# def resolve_status(user, task_name):
#     """
#     Позволяет отображать правильный статус в зависимости от имени группы пользователя
#     """
#     if Group.objects.filter(name=group_name, user=user).exists()