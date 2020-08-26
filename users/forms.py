from django import forms as f
from tasks.models import WorkType, WorkDirection
from users.models import User


class UserSettingsForm(f.ModelForm):
    work_types = f.ModelMultipleChoiceField(
        queryset=WorkType.objects,
        widget=f.CheckboxSelectMultiple,
    )
    work_directions = f.ModelMultipleChoiceField(
        queryset=WorkDirection.objects,
        widget=f.CheckboxSelectMultiple,
    )

    class Meta:
        fields = ['phone', 'work_types', 'work_directions']
        model = User

    def __init__(self, *args, **kwargs):
        """Для менеджера убираем work_types и work_directions"""
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.is_manager():
            del self.fields['work_types']
            del self.fields['work_directions']