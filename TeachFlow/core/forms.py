# core/forms.py
from django import forms
from .models import ClassGroup

class ClassGroupForm(forms.ModelForm):
    class Meta:
        model = ClassGroup
        fields = ['name', 'description', 'school', 'period', 'year', 'is_active']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-input'}),
            'description': forms.Textarea(attrs={'class': 'form-textarea', 'rows': 3}),
            'school': forms.TextInput(attrs={'class': 'form-input'}),
            'period': forms.Select(attrs={'class': 'form-select'}),
            'year': forms.NumberInput(attrs={'class': 'form-input'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-checkbox'}),
        }

    def __init__(self, *args, **kwargs):
        self.teacher = kwargs.pop('teacher', None)
        super().__init__(*args, **kwargs)

    def clean_name(self):
        name = self.cleaned_data['name']
        if ClassGroup.objects.filter(name=name, teacher=self.teacher).exclude(pk=self.instance.pk).exists():
            raise forms.ValidationError("Você já tem uma turma com esse nome.")
        return name
