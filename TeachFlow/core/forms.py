# core/forms.py
from django import forms
from .models import *

class ClassGroupForm(forms.ModelForm):
    class Meta:
        model = ClassGroup
        fields = ['name', 'description', 'school', 'period', 'schedule', 'year', 'is_active']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-input'}),
            'description': forms.Textarea(attrs={'class': 'form-textarea', 'rows': 3}),
            'school': forms.TextInput(attrs={'class': 'form-input'}),
            'period': forms.Select(attrs={'class': 'form-select'}),
            'schedule': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Ex: 07:30 - 08:20'}),
            'year': forms.NumberInput(attrs={'class': 'form-input'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-checkbox'}),
        }

    def __init__(self, *args, **kwargs):
        self.teacher = kwargs.pop('teacher', None)
        super().__init__(*args, **kwargs)

    def clean(self):
        cleaned_data = super().clean()

        name = cleaned_data.get('name')
        school = cleaned_data.get('school')
        year = cleaned_data.get('year')

        if name:
            name = name.strip()
            cleaned_data['name'] = name
        if not name:
            self.add_error(
                'name',
                'Informe o nome da turma.'
            )
        if school:
            school = school.strip()
            cleaned_data['school'] = school
        else:
            school = ''
        if not school:
            self.add_error(
                'school',
                'Informe o nome da escola.'
            )            

        if not self.teacher or not name or not school or year is None:
            return cleaned_data

        duplicate_class_group = ClassGroup.objects.filter(
            teacher=self.teacher,
            name__iexact=name,
            school__iexact=school,
            year=year,
        ).exclude(pk=self.instance.pk)

        if duplicate_class_group.exists():
            raise forms.ValidationError(
                'Você já possui uma turma com este nome, escola e ano letivo.'
            )

        return cleaned_data

class StudentForm(forms.ModelForm):
    class Meta:
        model = Student
        fields = ['first_name', 'last_name', 'birth_date', 'notes', 'is_active']  # Adicionado birth_date
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-input'}),
            'last_name': forms.TextInput(attrs={'class': 'form-input'}),
            'birth_date': forms.DateInput(attrs={
                'class': 'form-input', 
                'type': 'date',
                'placeholder': 'dd/mm/aaaa'
            }),  # NOVO WIDGET
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
    