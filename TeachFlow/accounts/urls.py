# accounts/urls.py
from django.urls import path, reverse_lazy
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_protect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import views as auth_views
from .views import validate_username_email
from .views import (
    ActivateAccountView,
    CustomLoginView,
    CustomLogoutView,
    ProfileView,
    ResendActivationEmailView,
    SignupCheckEmailView,
    SignupView,
)

urlpatterns = [
    path('register/', never_cache(csrf_protect(SignupView.as_view())), name='register'),
    path('register/check-email/', never_cache(SignupCheckEmailView.as_view()), name='signup_check_email'),
    path('register/resend-activation/', never_cache(csrf_protect(ResendActivationEmailView.as_view())), name='resend_activation_email'),
    path('activate/<str:token>/', never_cache(ActivateAccountView.as_view()), name='activate_account'),
    path('login/', never_cache(csrf_protect(CustomLoginView.as_view())), name='login'),
    path(
        'password-reset/',
        never_cache(auth_views.PasswordResetView.as_view(
            template_name='accounts/password_reset_form.html',
            email_template_name='accounts/emails/password_reset_email.txt',
            subject_template_name='accounts/emails/password_reset_subject.txt',
            success_url=reverse_lazy('password_reset_done'),
        )),
        name='password_reset',
    ),
    path(
        'password-reset/done/',
        never_cache(auth_views.PasswordResetDoneView.as_view(
            template_name='accounts/password_reset_done.html',
        )),
        name='password_reset_done',
    ),
    path(
        'password-reset/<uidb64>/<token>/',
        never_cache(auth_views.PasswordResetConfirmView.as_view(
            template_name='accounts/password_reset_confirm.html',
            success_url=reverse_lazy('password_reset_complete'),
        )),
        name='password_reset_confirm',
    ),
    path(
        'password-reset/complete/',
        never_cache(auth_views.PasswordResetCompleteView.as_view(
            template_name='accounts/password_reset_complete.html',
        )),
        name='password_reset_complete',
    ),
    path('logout/', never_cache(CustomLogoutView.as_view()), name='logout'),
    path('profile/', login_required(never_cache(ProfileView.as_view())), name='profile'),
    path('validate-username-email/', validate_username_email, name='validate_username_email'),
]
