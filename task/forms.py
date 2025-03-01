from django import forms
from .models import Task


class TaskForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = [
            "title",
            "description",
            "status",
            "priority",
            "due_date",
            "assigned_to",
        ]
        widgets = {
            "due_date": forms.DateInput(attrs={"type": "date"}),
            "description": forms.Textarea(attrs={"rows": 4}),
        }
