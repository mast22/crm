from django import forms as f
from .models import Task, TaskStatus


class CreateTaskForm(f.ModelForm):
    files = f.FileField(
        label='Файлы',
        widget=f.ClearableFileInput(attrs={'multiple': True}), required=False
    )

    class Meta:
        model = Task
        fields = [
            'customer_name',
            'phone',
            'whats_app',
            'email',
            'work_type',
            'work_direction',
            'name',
            'group',
            'teacher_name',
            'text',
            'files',
            'wanted_deadline',
            'promocode',
        ]

class ChangeTaskForm(f.ModelForm):
    class Meta:
        model = Task
        fields = [
            'name',
            'customer_name',
            'phone',
            'text',
            'whats_app',
            'email',
            'notes',
            'work_type',
            'work_direction',
        ]


class CreateTaskStatusForm(f.ModelForm):
    class Meta:
        model = TaskStatus
        fields = ['price', 'deadline']


class AddFileTaskForm(f.Form):
    files = f.FileField(
        widget=f.ClearableFileInput(attrs={'multiple': True}), required=False
    )

