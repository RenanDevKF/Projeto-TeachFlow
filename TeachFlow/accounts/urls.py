from django.urls import path
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
from . import views
from .views import (
    CustomLoginView, 
    CustomLogoutView,
    SignupView,
    ProfileUpdateView
)

urlpatterns = [
    # Registro (protegido contra CSRF, brute force e cache)
    path(
        'register/',
        csrf_protect(
            never_cache(
                require_http_methods(["GET", "POST"])(SignupView.as_view())
            )
        ),
        name='register'
    ),

    # Login (com headers de segurança e rate limiting implícito)
    path(
        'login/',
        csrf_protect(
            never_cache(
                require_http_methods(["GET", "POST"])(CustomLoginView.as_view())
            )
        ),
        name='login'
    ),

    # Logout (limpeza de sessão e headers)
    path(
        'logout/',
        never_cache(
            require_http_methods(["GET", "POST"])(CustomLogoutView.as_view())
        ),
        name='logout'
    ),

    # Perfil (acesso restrito a usuários logados + CSRF)
    path(
        'profile/',
        login_required(
            csrf_protect(
                never_cache(ProfileUpdateView.as_view())
            )
        ),
        name='profile'
    ),
]