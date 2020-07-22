from django import forms as f
from .models import Task


class CreateTaskForm(f.ModelForm):
    files = f.FileField(
        widget=f.ClearableFileInput(attrs={'multiple': True}), required=False
    )
    text = f.CharField(widget=f.Textarea)

    class Meta:
        model = Task
        fields = [
            'name',
            'phone',
            'whats_app',
            'email',
            'work_type',
            'address',
            'company',
            'text',
            'files',
            'wanted_deadline',
        ]
