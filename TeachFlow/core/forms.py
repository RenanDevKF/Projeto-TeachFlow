# core/forms.py
from django import forms
from django.utils import timezone
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
        self.duplicate_warning = False
        super().__init__(*args, **kwargs)

    def clean_birth_date(self):
        birth_date = self.cleaned_data.get('birth_date')

        if birth_date and birth_date > timezone.localdate():
            raise forms.ValidationError(
                'A data de nascimento não pode estar no futuro.'
            )

        return birth_date    
    
    def clean(self):
        cleaned_data = super().clean()

        first_name = cleaned_data.get('first_name')
        last_name = cleaned_data.get('last_name')
        birth_date = cleaned_data.get('birth_date')
        duplicate_confirmed = self.data.get('confirm_duplicate') == '1'

        if first_name:
            first_name = first_name.strip()
            cleaned_data['first_name'] = first_name

        if last_name:
            last_name = last_name.strip()
            cleaned_data['last_name'] = last_name

        if not first_name:
            self.add_error('first_name', 'Informe o primeiro nome do aluno.')

        if not last_name:
            self.add_error('last_name', 'Informe o sobrenome do aluno.')

        if not first_name or not last_name or not self.class_group:
            return cleaned_data

        students_with_same_name = Student.objects.filter(
            class_group=self.class_group,
            first_name__iexact=first_name,
            last_name__iexact=last_name,
        ).exclude(pk=self.instance.pk)

        if birth_date and students_with_same_name.filter(birth_date=birth_date).exists():
            raise forms.ValidationError(
                'Já existe nesta turma um aluno com o mesmo nome e a mesma data de nascimento.'
            )

        needs_confirmation = students_with_same_name.exists() and (
            birth_date is None or
            students_with_same_name.filter(birth_date__isnull=True).exists()
        )

        if needs_confirmation and not duplicate_confirmed:
            self.duplicate_warning = True
            raise forms.ValidationError(
                'Já existe um aluno com este nome nesta turma. Confirme o cadastro caso sejam pessoas diferentes.'
            )

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
            self.fields['exercises'].queryset = Exercise.objects.filter(created_by=teacher, is_template=False, is_active=True,)
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
            'duration': forms.NumberInput(attrs={'class': 'form-input', 'min': 1, 'max': 1440, 'step': 1, 'placeholder': 'Ex.: 50'}),
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
    