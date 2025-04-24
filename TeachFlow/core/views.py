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
    
@method_decorator(csrf_protect, name='dispatch')
class ClassGroupDeleteView(LoginRequiredMixin, TeacherRequiredMixin, OwnershipRequiredMixin, DeleteView):
    model = ClassGroup
    template_name = 'core/class_group_confirm_delete.html'
    success_url = reverse_lazy('class-group-list')
    
    def delete(self, request, *args, **kwargs):
        messages.success(request, "Class group deleted successfully.")
        return super().delete(request, *args, **kwargs)
    
# Lesson Views
@method_decorator(csrf_protect, name='dispatch')
class LessonListView(LoginRequiredMixin, TeacherRequiredMixin, ListView):
    model = Lesson
    template_name = 'core/lesson_list.html'
    context_object_name = 'lessons'
    
    def get_queryset(self):
        class_group_id = self.kwargs.get('class_group_id')
        return Lesson.objects.filter(class_group_id=class_group_id, 
                                     class_group__teacher=self.request.user.teacher_profile)


@method_decorator(csrf_protect, name='dispatch')
class LessonDetailView(LoginRequiredMixin, TeacherRequiredMixin, OwnershipRequiredMixin, DetailView):
    model = Lesson
    template_name = 'core/lesson_detail.html'
    context_object_name = 'lesson'


@method_decorator(csrf_protect, name='dispatch')
class LessonCreateView(LoginRequiredMixin, TeacherRequiredMixin, CreateView):
    model = Lesson
    template_name = 'core/lesson_form.html'
    fields = ['date', 'title', 'content', 'performance_notes', 'objectives', 'tags']
    
    def dispatch(self, request, *args, **kwargs):
        # Security check: verify class group belongs to this teacher
        self.class_group = get_object_or_404(
            ClassGroup, 
            pk=self.kwargs.get('class_group_id'),
            teacher=self.request.user.teacher_profile
        )
        return super().dispatch(request, *args, **kwargs)
    
    def form_valid(self, form):
        form.instance.class_group = self.class_group
        messages.success(self.request, "Lesson created successfully!")
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse_lazy('lesson-detail', kwargs={'pk': self.object.pk})


@method_decorator(csrf_protect, name='dispatch')
class LessonUpdateView(LoginRequiredMixin, TeacherRequiredMixin, OwnershipRequiredMixin, UpdateView):
    model = Lesson
    template_name = 'core/lesson_form.html'
    fields = ['date', 'title', 'content', 'performance_notes', 'objectives', 'tags']
    
    def get_success_url(self):
        return reverse_lazy('lesson-detail', kwargs={'pk': self.object.pk})


@method_decorator(csrf_protect, name='dispatch')
class LessonDeleteView(LoginRequiredMixin, TeacherRequiredMixin, OwnershipRequiredMixin, DeleteView):
    model = Lesson
    template_name = 'core/lesson_confirm_delete.html'
    
    def get_success_url(self):
        return reverse_lazy('lesson-list', kwargs={'class_group_id': self.object.class_group_id})
    
# Exercise Views
@method_decorator(csrf_protect, name='dispatch')
class ExerciseCreateView(LoginRequiredMixin, TeacherRequiredMixin, CreateView):
    model = Exercise
    template_name = 'core/exercise_form.html'
    fields = ['title', 'description', 'duration', 'materials', 'objectives', 'tags']
    
    def dispatch(self, request, *args, **kwargs):
        # Security check: verify lesson belongs to this teacher
        self.lesson = get_object_or_404(
            Lesson, 
            pk=self.kwargs.get('lesson_id'),
            class_group__teacher=self.request.user.teacher_profile
        )
        return super().dispatch(request, *args, **kwargs)
    
    def form_valid(self, form):
        form.instance.lesson = self.lesson
        messages.success(self.request, "Exercise added successfully!")
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse_lazy('lesson-detail', kwargs={'pk': self.lesson.pk})
    
# Learning Objective Views
@method_decorator(csrf_protect, name='dispatch')
class LearningObjectiveListView(LoginRequiredMixin, TeacherRequiredMixin, ListView):
    model = LearningObjective
    template_name = 'core/learning_objective_list.html'
    context_object_name = 'objectives'
    
    def get_queryset(self):
        return LearningObjective.objects.filter(teacher=self.request.user.teacher_profile)


@method_decorator(csrf_protect, name='dispatch')
class LearningObjectiveCreateView(LoginRequiredMixin, TeacherRequiredMixin, CreateView):
    model = LearningObjective
    template_name = 'core/learning_objective_form.html'
    fields = ['title', 'description', 'tags']
    success_url = reverse_lazy('objective-list')
    
    def form_valid(self, form):
        form.instance.teacher = self.request.user.teacher_profile
        messages.success(self.request, "Learning objective created successfully!")
        return super().form_valid(form)
    
# Future Ideas Views
@method_decorator(csrf_protect, name='dispatch')
class FutureIdeaListView(LoginRequiredMixin, TeacherRequiredMixin, ListView):
    model = FutureIdea
    template_name = 'core/future_idea_list.html'
    context_object_name = 'ideas'
    
    def get_queryset(self):
        return FutureIdea.objects.filter(teacher=self.request.user.teacher_profile)


@method_decorator(csrf_protect, name='dispatch')
class FutureIdeaCreateView(LoginRequiredMixin, TeacherRequiredMixin, CreateView):
    model = FutureIdea
    template_name = 'core/future_idea_form.html'
    fields = ['title', 'description', 'class_group', 'tags']
    success_url = reverse_lazy('idea-list')
    
    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        # Limit class group choices to only those owned by this teacher
        form.fields['class_group'].queryset = ClassGroup.objects.filter(
            teacher=self.request.user.teacher_profile
        )
        return form
    
    def form_valid(self, form):
        form.instance.teacher = self.request.user.teacher_profile
        messages.success(self.request, "Future idea created successfully!")
        return super().form_valid(form)