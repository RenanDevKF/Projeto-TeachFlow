from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy
from django.shortcuts import redirect, get_object_or_404
from django.contrib import messages
from django.db.models import Q
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_protect

from .models import ClassGroup, Student, Lesson, Exercise, Tag, LearningObjective, FutureIdea


class TeacherRequiredMixin(UserPassesTestMixin):
    """Ensure that only teachers can access specific views"""
    def test_func(self):
        return hasattr(self.request.user, 'teacher_profile')
    
    def handle_no_permission(self):
        messages.error(self.request, "You must be a teacher to access this page.")
        return redirect('login')