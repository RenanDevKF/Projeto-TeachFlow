# accounts/urls.py
from django.urls import path
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_protect
from django.contrib.auth.decorators import login_required
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
    path('logout/', never_cache(CustomLogoutView.as_view()), name='logout'),
    path('profile/', login_required(never_cache(ProfileView.as_view())), name='profile'),
    path('validate-username-email/', validate_username_email, name='validate_username_email'),
]
