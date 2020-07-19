from django import forms as f
from .models import Comment, Task


class CreateTaskForm(f.ModelForm):
    files = f.FileField(
        widget=f.ClearableFileInput(attrs={'multiple': True}), required=False
    )
    name = f.CharField()
    text = f.CharField(widget=f.Textarea)

    class Meta:
        model = Task
        fields = ['name', 'text', 'files']


class CreateCommentForm(f.ModelForm):
    files = f.FileField(
        widget=f.ClearableFileInput(attrs={'multiple': True}), required=False
    )

    class Meta:
        model = Comment
        fields = ['text', 'files']
