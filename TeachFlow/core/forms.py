# core/forms.py
from django import forms
from .models import *

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

class StudentForm(forms.ModelForm):
    class Meta:
        model = Student
        fields = ['first_name', 'last_name', 'notes', 'is_active']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-input'}),
            'last_name': forms.TextInput(attrs={'class': 'form-input'}),
            'notes': forms.Textarea(attrs={'class': 'form-textarea', 'rows': 3}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-checkbox'}),
        }

    def __init__(self, *args, **kwargs):
        self.class_group = kwargs.pop('class_group', None)
        super().__init__(*args, **kwargs)
    
    def clean(self):
        cleaned_data = super().clean()
        first_name = cleaned_data.get('first_name')
        last_name = cleaned_data.get('last_name')
        
        # Verifica se já existe um aluno com o mesmo nome na turma
        if first_name and last_name and self.class_group:
            if Student.objects.filter(
                first_name=first_name,
                last_name=last_name,
                class_group=self.class_group
            ).exclude(pk=self.instance.pk).exists():
                raise forms.ValidationError("Já existe um aluno com este nome nesta turma.")
        
        return cleaned_data
    
class LessonForm(forms.ModelForm):
    class Meta:
        model = Lesson
        fields = ['class_group', 'date', 'title', 'content', 'performance_notes', 'exercises', 'tags']
        widgets = {
            'date': forms.DateInput(attrs={'class': 'form-input'}),
            'title': forms.TextInput(attrs={'class': 'form-input'}),
            'content': forms.Textarea(attrs={'class': 'form-textarea', 'rows': 4}),
            'performance_notes': forms.Textarea(attrs={'class': 'form-textarea', 'rows': 3}),
            'exercises': forms.SelectMultiple(attrs={'class': 'hidden'}),  # Nosso custom widget vai cuidar disso
            'tags': forms.SelectMultiple(attrs={'class': 'hidden'}),  # Nosso custom widget vai cuidar disso
        }

    def __init__(self, *args, **kwargs):
        teacher = kwargs.pop('teacher', None)
        super().__init__(*args, **kwargs)
        
        if teacher:
            self.fields['exercises'].queryset = Exercise.objects.filter(created_by=teacher)
            self.fields['class_group'].queryset = ClassGroup.objects.filter(teacher=teacher)
            # Filtra tags apenas do tipo 'lesson' ou 'general'
            self.fields['tags'].queryset = Tag.objects.filter(
                teacher=teacher,
                type__in=['lesson', 'general']
            ).distinct()
            
class ExerciseForm(forms.ModelForm):
    class Meta:
        model = Exercise
        fields = ['title', 'description', 'duration', 'materials', 'objectives', 'tags', 'is_template']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-input'}),
            'description': forms.Textarea(attrs={'class': 'form-textarea', 'rows': 4}),
            'duration': forms.NumberInput(attrs={'class': 'form-input'}),
            'materials': forms.Textarea(attrs={'class': 'form-textarea', 'rows': 3}),
            'objectives': forms.SelectMultiple(attrs={'class': 'hidden'}),  # Custom widget
            'tags': forms.SelectMultiple(attrs={'class': 'hidden'}),  # Custom widget
        }

    def __init__(self, *args, **kwargs):
        teacher = kwargs.pop('teacher', None)
        super().__init__(*args, **kwargs)
        if teacher:
            self.fields['objectives'].queryset = LearningObjective.objects.filter(teacher=teacher)
            # Filtra tags apenas do tipo 'exercise' ou 'general'
            self.fields['tags'].queryset = Tag.objects.filter(
                teacher=teacher,
                type__in=['exercise', 'general']
            ).distinct()
    