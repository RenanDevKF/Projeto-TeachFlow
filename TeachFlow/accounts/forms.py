# accounts/forms.py
from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser, Teacher
from django.core.exceptions import ValidationError

class CustomUserCreationForm(UserCreationForm):
    username = forms.CharField(
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    first_name = forms.CharField(
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    last_name = forms.CharField(
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={'class': 'form-control'})
    )
    password1 = forms.CharField(
        label="Password",
        widget=forms.PasswordInput(attrs={'class': 'form-control'})
    )
    password2 = forms.CharField(
        label="Password confirmation",
        widget=forms.PasswordInput(attrs={'class': 'form-control'})
    )

    class Meta:
        model = CustomUser
        fields = ('username', 'email', 'first_name', 'last_name', 'password1', 'password2')
        
    def clean_username(self):
        username = self.cleaned_data.get('username')
        if CustomUser.objects.filter(username=username).exists():
            raise ValidationError("Este nome de usuário já está em uso.")
        return username

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if CustomUser.objects.filter(email=email).exists():
            raise ValidationError("Este email já está em uso")
        return email

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ('first_name', 'last_name', 'username')

    def clean_first_name(self):
        first_name = self.cleaned_data.get('first_name', '').strip()

        if not first_name:
            raise ValidationError("Informe seu nome.")

        return first_name

    def clean_last_name(self):
        last_name = self.cleaned_data.get('last_name', '').strip()

        if not last_name:
            raise ValidationError("Informe seu sobrenome.")

        return last_name

    def clean_username(self):
        username = self.cleaned_data.get('username', '').strip()

        if not username:
            raise ValidationError("Informe um nome de usuário.")

        if CustomUser.objects.filter(username__iexact=username).exclude(pk=self.instance.pk).exists():
            raise ValidationError("Este nome de usuário já está em uso.")

        return username


class TeacherProfileForm(forms.ModelForm):
    class Meta:
        model = Teacher
        fields = ('display_name', 'subject_area')

    def clean_display_name(self):
        return self.cleaned_data.get('display_name', '').strip()

    def clean_subject_area(self):
        return self.cleaned_data.get('subject_area', '').strip()
    
class ChangeEmailForm(forms.Form):
    new_email = forms.EmailField(label='Novo e-mail')
    current_password = forms.CharField(
        label='Senha atual',
        widget=forms.PasswordInput,
    )

    def __init__(self, user, *args, **kwargs):
        self.user = user
        super().__init__(*args, **kwargs)

    def clean_new_email(self):
        new_email = self.cleaned_data.get('new_email', '').strip().lower()

        if new_email == self.user.email.lower():
            raise ValidationError("O novo e-mail deve ser diferente do e-mail atual.")

        if CustomUser.objects.filter(email__iexact=new_email).exclude(pk=self.user.pk).exists():
            raise ValidationError("Este e-mail já está em uso.")

        return new_email

    def clean_current_password(self):
        current_password = self.cleaned_data.get('current_password')

        if not self.user.check_password(current_password):
            raise ValidationError("Senha atual incorreta.")

        return current_password