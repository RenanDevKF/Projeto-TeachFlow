# accounts/forms.py
from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import CustomUser, Teacher
from django.core.exceptions import ValidationError
from .utils import normalize_email, normalize_username, validate_username

class CustomAuthenticationForm(AuthenticationForm):
    username = forms.CharField(
        label='E-mail ou nome de usuário',
        widget=forms.TextInput(
            attrs={
                'autofocus': True,
                'autocomplete': 'username',
                'placeholder': 'seu@email.com ou usuário',
            }
        ),
    )

    password = forms.CharField(
        label='Senha',
        strip=False,
        widget=forms.PasswordInput(
            attrs={
                'autocomplete': 'current-password',
                'placeholder': '••••••••',
            }
        ),
    )

    error_messages = {
        'invalid_login': 'E-mail, nome de usuário ou senha inválidos.',
        'inactive': 'Esta conta está inativa.',
    }

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

    class Meta:
        model = CustomUser
        fields = ('username', 'email', 'first_name', 'last_name', 'password1', 'password2')
        
    def clean_username(self):
        username = normalize_username(
            self.cleaned_data.get('username')
        )

        validation_error = validate_username(username)

        if validation_error:
            raise ValidationError(validation_error)

        if CustomUser.objects.filter(username__iexact=username).exists():
            raise ValidationError("Este nome de usuário já está em uso.")

        return username

    def clean_email(self):
        email = normalize_email(
            self.cleaned_data.get('email')
        )

        if CustomUser.objects.filter(email__iexact=email).exists():
            raise ValidationError("Este e-mail já está em uso.")

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
        username = normalize_username(
            self.cleaned_data.get('username')
        )

        if not username:
            raise ValidationError("Informe um nome de usuário.")

        validation_error = validate_username(username)

        if validation_error:
            raise ValidationError(validation_error)

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
        new_email = normalize_email(self.cleaned_data.get('new_email'))

        if new_email == normalize_email(self.user.email):
            raise ValidationError("O novo e-mail deve ser diferente do e-mail atual.")

        if CustomUser.objects.filter(email__iexact=new_email).exclude(pk=self.user.pk).exists():
            raise ValidationError("Este e-mail já está em uso.")

        return new_email

    def clean_current_password(self):
        current_password = self.cleaned_data.get('current_password')

        if not self.user.check_password(current_password):
            raise ValidationError("Senha atual incorreta.")

        return current_password