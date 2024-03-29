from django import forms as f
from .models import Comment

class CreateCommentForm(f.ModelForm):
    files = f.FileField(
        widget=f.ClearableFileInput(attrs={'multiple': True}), required=False
    )

    class Meta:
        model = Comment
        fields = ['text', 'files']

class AddFileForm(f.Form):
    files = f.FileField(
        widget=f.ClearableFileInput(attrs={'multiple': True}), required=False
    )
