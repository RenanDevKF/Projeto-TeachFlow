# accounts/urls.py
from django.urls import path
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_protect
from django.contrib.auth.decorators import login_required
from .views import (
    CustomLoginView, 
    CustomLogoutView,
    SignupView,
    ProfileUpdateView
)

urlpatterns = [
    path('register/', never_cache(csrf_protect(SignupView.as_view())), name='register'),
    path('login/', never_cache(csrf_protect(CustomLoginView.as_view())), name='login'),
    path('logout/', never_cache(CustomLogoutView.as_view()), name='logout'),
    path('profile/', login_required(never_cache(ProfileUpdateView.as_view())), name='profile'),
]
