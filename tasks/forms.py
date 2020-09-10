from django import forms as f
from .models import Task, TaskStatus


class CreateTaskForm(f.ModelForm):
    files = f.FileField(
        widget=f.ClearableFileInput(attrs={'multiple': True}), required=False
    )
    text = f.CharField(widget=f.Textarea)

    class Meta:
        model = Task
        fields = [
            'name',
            'customer_name',
            'phone',
            'whats_app',
            'email',
            'work_type',
            'work_direction',
            'text',
            'group',
            'files',
            'teacher_name',
            'wanted_deadline',
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


class RateTaskForm(f.ModelForm):
    class Meta:
        model = TaskStatus
        fields = ['price', 'deadline']
        # widgets = {'task': f.HiddenInput()}


class AddFileTaskForm(f.Form):
    files = f.FileField(
        widget=f.ClearableFileInput(attrs={'multiple': True}), required=False
    )