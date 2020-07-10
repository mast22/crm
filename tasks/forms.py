from django import forms as f
from .models import Comment, Task


class CreateTaskForm(f.ModelForm):
    files = f.FileField(widget=f.ClearableFileInput(attrs={'multiple': True}))
    name = f.CharField()
    text = f.CharField(widget=f.Textarea)

    class Meta:
        model = Task
        fields = ['files', 'name', 'text']


class CreateCommentForm(f.ModelForm):
    class Meta:
        model = Comment
        fields = ['text']
