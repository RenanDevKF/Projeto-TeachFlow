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
    
class OwnershipRequiredMixin:
    """Ensure users can only access their own data"""
    def get_queryset(self):
        # Filter queryset to only include objects owned by the current user
        base_qs = super().get_queryset()
        if hasattr(self.model, 'teacher'):
            return base_qs.filter(teacher=self.request.user.teacher_profile)
        elif hasattr(self.model, 'class_group'):
            return base_qs.filter(class_group__teacher=self.request.user.teacher_profile)
        return base_qs.none()  # Fallback to empty queryset if no ownership relation exists

# Class Group Views
@method_decorator(csrf_protect, name='dispatch')
class ClassGroupListView(LoginRequiredMixin, TeacherRequiredMixin, ListView):
    model = ClassGroup
    template_name = 'core/class_group_list.html'
    context_object_name = 'class_groups'
    
    def get_queryset(self):
        return ClassGroup.objects.filter(teacher=self.request.user.teacher_profile)
    
@method_decorator(csrf_protect, name='dispatch')
class ClassGroupDetailView(LoginRequiredMixin, TeacherRequiredMixin, OwnershipRequiredMixin, DetailView):
    model = ClassGroup
    template_name = 'core/class_group_detail.html'
    context_object_name = 'class_group'
    
@method_decorator(csrf_protect, name='dispatch')
class ClassGroupCreateView(LoginRequiredMixin, TeacherRequiredMixin, CreateView):
    model = ClassGroup
    template_name = 'core/class_group_form.html'
    fields = ['name', 'description', 'year', 'is_active']
    success_url = reverse_lazy('class-group-list')
    
    def form_valid(self, form):
        form.instance.teacher = self.request.user.teacher_profile
        messages.success(self.request, "Class group created successfully!")
        return super().form_valid(form)
    
@method_decorator(csrf_protect, name='dispatch')
class ClassGroupUpdateView(LoginRequiredMixin, TeacherRequiredMixin, OwnershipRequiredMixin, UpdateView):
    model = ClassGroup
    template_name = 'core/class_group_form.html'
    fields = ['name', 'description', 'year', 'is_active']
    
    def get_success_url(self):
        return reverse_lazy('class-group-detail', kwargs={'pk': self.object.pk})