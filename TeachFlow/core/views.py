from django.template import context
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, View, TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from django.urls import reverse_lazy, reverse
from django.shortcuts import redirect, get_object_or_404, render
from django.contrib import messages
from django.db import transaction
from django.db.models import Q, Case, IntegerField, Value, When, Count
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_protect, csrf_exempt
from django.views.decorators.http import require_POST
from django.http import JsonResponse, Http404, HttpResponseRedirect
from datetime import date
from .models import ClassGroup, Student, Lesson, Exercise, Tag, LearningObjective, FutureIdea, LessonExercise
from .forms import *
from django.utils import timezone
from datetime import date
import json
import re

class TeacherRequiredMixin(UserPassesTestMixin):
    """Ensure that only teachers can access specific views"""
    def test_func(self):
        return hasattr(self.request.user, 'teacher_profile')
    
    def handle_no_permission(self):
        messages.error(self.request, "Voce precisa ser um professor para acessar essa pagina.")
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
    
    
@login_required
def dashboard_view(request):
    # Se for superusuário, redireciona para o admin
    if request.user.is_superuser:
        return redirect('admin:index')
    
    # Verifica se o usuário tem perfil de professor
    if not hasattr(request.user, 'teacher_profile'):
        messages.error(request, "Acesso restrito a professores.")
        logout(request)  # Desloga o usuário para evitar loops
        return redirect('login')
    
    teacher = request.user.teacher_profile
    today_lessons = Lesson.objects.filter(date=date.today(), class_group__teacher=teacher)
    class_groups = ClassGroup.objects.filter(teacher=teacher)
    
    return render(request, 'dashboard/dashboard.html', {
        'today': timezone.now(),
        'today_lessons': today_lessons,
        'class_groups': class_groups
    })

# Class Group Views
@method_decorator(csrf_protect, name='dispatch')
class ClassGroupListView(LoginRequiredMixin, TeacherRequiredMixin, ListView):
    model = ClassGroup
    template_name = 'classes/class_group_list.html'
    context_object_name = 'class_groups'
    
    def get_selected_status(self):
        status = self.request.GET.get('status', 'active')

        if status not in {'active', 'archived', 'all'}:
            status = 'active'
        return status    
    
    def get_queryset(self):
        queryset = ClassGroup.objects.filter(
            teacher=self.request.user.teacher_profile
        ).prefetch_related('students', 'lessons')
        
        status = self.get_selected_status()
        
        # Adicione os filtros aqui
        search = self.request.GET.get('search')
        school = self.request.GET.get('school')
        year = self.request.GET.get('year')
        period = self.request.GET.get('period')
        
        if status == 'active':
            queryset = queryset.filter(is_active=True)

        elif status == 'archived':
            queryset = queryset.filter(is_active=False)        
        
        if search:
            queryset = queryset.filter(
                Q(name__icontains=search) |
                Q(description__icontains=search) |
                Q(school__icontains=search)
            )
        
        if school:
            queryset = queryset.filter(school__icontains=school)
            
        if year:
            queryset = queryset.filter(year=year)
            
        if period:
            queryset = queryset.filter(period=period)
            
        queryset = queryset.annotate(
            period_order=Case(
                When(period='Manhã', then=Value(1)),
                When(period='Tarde', then=Value(2)),
                When(period='Noite', then=Value(3)),
                default=Value(4),
                output_field=IntegerField(),
            )
        ).order_by('period_order', 'schedule', 'name')  
                  
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Adicione os valores atuais dos filtros ao contexto
        context['search'] = self.request.GET.get('search', '')
        context['school'] = self.request.GET.get('school', '')
        context['year'] = self.request.GET.get('year', '')
        context['period'] = self.request.GET.get('period', '')
        context['selected_status'] = self.get_selected_status()
        
        teacher_class_groups = ClassGroup.objects.filter(
            teacher=self.request.user.teacher_profile
        )

        context['has_any_class_groups'] = teacher_class_groups.exists()
        context['has_active_class_groups'] = teacher_class_groups.filter(
            is_active=True
        ).exists()
        context['has_archived_class_groups'] = teacher_class_groups.filter(
            is_active=False
        ).exists()
        return context
    
@method_decorator(csrf_protect, name='dispatch')
class ClassGroupDetailView(LoginRequiredMixin, TeacherRequiredMixin, OwnershipRequiredMixin, DetailView):
    model = ClassGroup
    template_name = 'classes/class_group_detail.html'
    context_object_name = 'class_group'
    
@method_decorator(csrf_protect, name='dispatch')
class ClassGroupCreateView(LoginRequiredMixin, TeacherRequiredMixin, CreateView):
    model = ClassGroup
    template_name = 'classes/class_group_form.html'
    form_class = ClassGroupForm
    success_url = reverse_lazy('class_group_list')
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['teacher'] = self.request.user.teacher_profile
        return kwargs
    
    def form_valid(self, form):
        form.instance.teacher = self.request.user.teacher_profile
        messages.success(self.request, "Turma criada com sucesso!")
        return super().form_valid(form)
    
@method_decorator(csrf_protect, name='dispatch')
class ClassGroupUpdateView(LoginRequiredMixin, TeacherRequiredMixin, OwnershipRequiredMixin, UpdateView):
    model = ClassGroup
    template_name = 'classes/class_group_form.html'
    form_class = ClassGroupForm
    success_url = reverse_lazy('class_group_list')
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['teacher'] = self.request.user.teacher_profile
        return kwargs
    
    def get_success_url(self):
        return reverse_lazy('class_group_detail', kwargs={'pk': self.object.pk})


@method_decorator(csrf_protect, name='dispatch')
class ClassGroupArchiveView(LoginRequiredMixin, TeacherRequiredMixin, View):
    def post(self, request, pk):
        class_group = get_object_or_404(
            ClassGroup,
            pk=pk,
            teacher=request.user.teacher_profile,
        )

        if not class_group.is_active:
            messages.info(request, "Esta turma já está arquivada.")
            return redirect('class_group_detail', pk=class_group.pk)

        class_group.is_active = False
        class_group.save(update_fields=['is_active', 'updated_at'])

        messages.success(
            request,
            "Turma arquivada com sucesso. Os alunos, as aulas e os demais registros foram preservados.",
        )
        return redirect('class_group_detail', pk=class_group.pk)


@method_decorator(csrf_protect, name='dispatch')
class ClassGroupRestoreView(LoginRequiredMixin, TeacherRequiredMixin, View):
    def post(self, request, pk):
        class_group = get_object_or_404(
            ClassGroup,
            pk=pk,
            teacher=request.user.teacher_profile,
        )

        if class_group.is_active:
            messages.info(request, "Esta turma já está ativa.")
            return redirect('class_group_detail', pk=class_group.pk)

        class_group.is_active = True
        class_group.save(update_fields=['is_active', 'updated_at'])

        messages.success(request, "Turma reativada com sucesso.")
        return redirect('class_group_detail', pk=class_group.pk)


@method_decorator(csrf_protect, name='dispatch')
class ClassGroupDeleteView(LoginRequiredMixin, TeacherRequiredMixin, OwnershipRequiredMixin, DeleteView):
    model = ClassGroup
    template_name = 'classes/class_group_confirm_delete.html'
    success_url = reverse_lazy('class_group_list')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        context['class_group'] = self.object # Garante que o objeto está no contexto
        context['students_count'] = self.object.students.count()
        context['lessons_count'] = self.object.lessons.count()
        return context
    
    def delete(self, request, *args, **kwargs):
        messages.success(request, "Turma excluída com sucesso.")
        return super().delete(request, *args, **kwargs)
    
@method_decorator(csrf_protect, name='dispatch')
class LessonListView(LoginRequiredMixin, TeacherRequiredMixin, ListView):
    model = Lesson
    template_name = 'lessons/lesson_list.html'
    context_object_name = 'lessons'
    paginate_by = 10

    VALID_SECTIONS = {'upcoming', 'pending', 'completed', 'cancelled'}

    def dispatch(self, request, *args, **kwargs):
        self.class_group = None
        class_group_id = self.kwargs.get('class_group_id')

        if class_group_id:
            self.class_group = get_object_or_404(ClassGroup, pk=class_group_id, teacher=request.user.teacher_profile)

        return super().dispatch(request, *args, **kwargs)

    def get_selected_section(self):
        section = self.request.GET.get('section', 'upcoming')

        if section not in self.VALID_SECTIONS:
            return 'upcoming'

        return section

    def get_selected_class_group(self):
        if self.class_group:
            return str(self.class_group.pk)

        class_group_id = self.request.GET.get('class', '')
        return class_group_id if class_group_id.isdigit() else ''

    def get_filtered_queryset(self):
        teacher = self.request.user.teacher_profile
        queryset = Lesson.objects.filter(class_group__teacher=teacher).select_related('class_group').prefetch_related('tags')

        if self.class_group:
            queryset = queryset.filter(class_group=self.class_group)
        else:
            selected_class_group = self.get_selected_class_group()

            if selected_class_group:
                queryset = queryset.filter(class_group_id=selected_class_group)

        tag_id = self.request.GET.get('tag', '')
        date_filter = self.request.GET.get('date', '')

        if tag_id.isdigit():
            queryset = queryset.filter(tags__id=tag_id)

        if date_filter:
            queryset = queryset.filter(date=date_filter)

        return queryset.distinct()

    def get_queryset(self):
        queryset = self.get_filtered_queryset()
        section = self.get_selected_section()
        today = timezone.localdate()

        if section == 'upcoming':
            queryset = queryset.filter(status=Lesson.Status.PLANNED, date__gte=today).order_by('date', 'title', 'id')
        elif section == 'pending':
            queryset = queryset.filter(status=Lesson.Status.PLANNED, date__lt=today).order_by('-date', 'title', 'id')
        elif section == 'completed':
            queryset = queryset.filter(status=Lesson.Status.COMPLETED).order_by('-date', 'title', 'id')
        else:
            queryset = queryset.filter(status=Lesson.Status.CANCELLED).order_by('-date', 'title', 'id')

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        teacher = self.request.user.teacher_profile
        today = timezone.localdate()
        filtered_lessons = self.get_filtered_queryset()

        query_parameters = self.request.GET.copy()
        query_parameters.pop('page', None)

        context['class_group'] = self.class_group
        context['is_class_group_scope'] = self.class_group is not None
        context['selected_section'] = self.get_selected_section()
        context['selected_class_group'] = self.get_selected_class_group()
        context['selected_tag'] = self.request.GET.get('tag', '')
        context['selected_date'] = self.request.GET.get('date', '')
        context['has_active_filters'] = bool(
            context['selected_tag']
            or context['selected_date']
            or (
                context['selected_class_group']
                and not context['is_class_group_scope']
            )
        )
        context['today'] = today
        context['query_string'] = query_parameters.urlencode()

        context['class_groups'] = ClassGroup.objects.filter(teacher=teacher).order_by('-is_active', 'name', 'year')
        context['tags'] = Tag.objects.filter(teacher=teacher, type__in=['lesson', 'general']).distinct().order_by('name')

        context['upcoming_count'] = filtered_lessons.filter(status=Lesson.Status.PLANNED, date__gte=today).count()
        context['pending_count'] = filtered_lessons.filter(status=Lesson.Status.PLANNED, date__lt=today).count()
        context['completed_count'] = filtered_lessons.filter(status=Lesson.Status.COMPLETED).count()
        context['cancelled_count'] = filtered_lessons.filter(status=Lesson.Status.CANCELLED).count()
        context['has_any_lessons'] = Lesson.objects.filter(class_group__teacher=teacher).exists()

        if context.get('paginator'):
            context['results_count'] = context['paginator'].count
        else:
            context['results_count'] = len(context['lessons'])

        return context

@method_decorator(csrf_protect, name='dispatch')
class LessonDetailView(LoginRequiredMixin, TeacherRequiredMixin, OwnershipRequiredMixin, DetailView):
    model = Lesson
    template_name = 'lessons/lesson_detail.html'
    context_object_name = 'lesson'

    def get_queryset(self):
        return Lesson.objects.filter(class_group__teacher=self.request.user.teacher_profile).select_related(
            'class_group',
        ).prefetch_related(
            'tags',
            'exercises__tags',
            'exercises__objectives',
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        applied_exercises = list(self.object.lesson_exercises.filter(is_applied=True).values_list('exercise_id', flat=True))

        applied_exercises_count = len(applied_exercises)
        total_exercises_count = self.object.lesson_exercises.count()
        applied_exercises_percentage = round((applied_exercises_count / total_exercises_count) * 100) if total_exercises_count else 0
        lesson_objectives = LearningObjective.objects.filter(
            teacher=self.request.user.teacher_profile,
            exercises__lessons=self.object,
        ).distinct().order_by('title')

        context['today'] = timezone.localdate()
        context['applied_exercises'] = applied_exercises
        context['applied_exercises_count'] = applied_exercises_count
        context['total_exercises_count'] = total_exercises_count
        context['applied_exercises_percentage'] = applied_exercises_percentage
        context['lesson_objectives'] = lesson_objectives

        return context

@method_decorator(csrf_protect, name='dispatch')
class LessonCreateView(LoginRequiredMixin, TeacherRequiredMixin, CreateView):
    model = Lesson
    form_class = LessonForm
    template_name = 'lessons/lesson_form.html'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['teacher'] = self.request.user.teacher_profile
        return kwargs

    def form_valid(self, form):
        response = super().form_valid(form)

        messages.success(
            self.request,
            {
                Lesson.Status.PLANNED: 'Aula planejada com sucesso.',
                Lesson.Status.COMPLETED: 'Aula registrada como realizada com sucesso.',
                Lesson.Status.CANCELLED: 'Aula cancelada com sucesso.',
            }[self.object.status]
        )

        return response

    def get_success_url(self):
        return reverse('lesson_detail', kwargs={'pk': self.object.pk})
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.object:
            context['selected_tags'] = self.object.tags.values_list('id', flat=True)
        else:
            context['selected_tags'] = []
        return context


@method_decorator(csrf_protect, name='dispatch')
class LessonUpdateView(LoginRequiredMixin, TeacherRequiredMixin, OwnershipRequiredMixin, UpdateView):
    model = Lesson
    form_class = LessonForm
    template_name = 'lessons/lesson_form.html'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['teacher'] = self.request.user.teacher_profile
        return kwargs

    def form_valid(self, form):
        response = super().form_valid(form)

        messages.success(
            self.request,
            {
                Lesson.Status.PLANNED: 'Aula salva como planejada.',
                Lesson.Status.COMPLETED: 'Aula registrada como realizada.',
                Lesson.Status.CANCELLED: 'Aula registrada como cancelada.',
            }[self.object.status]
        )

        return response

    def get_success_url(self):
        return reverse('lesson_detail', kwargs={'pk': self.object.pk})
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.object:
            context['selected_tags'] = self.object.tags.values_list('id', flat=True)
        else:
            context['selected_tags'] = []
        return context


@method_decorator(csrf_protect, name='dispatch')
class LessonDeleteView(LoginRequiredMixin, TeacherRequiredMixin, OwnershipRequiredMixin, DeleteView):
    model = Lesson
    template_name = 'lessons/lesson_confirm_delete.html'
    context_object_name = 'lesson'

    def get_queryset(self):
        return Lesson.objects.filter(
            class_group__teacher=self.request.user.teacher_profile
        ).select_related('class_group')

    def get_success_url(self):
        return reverse(
            'group_lessons',
            kwargs={'class_group_id': self.object.class_group_id},
        )
    
@method_decorator(csrf_protect, name='dispatch')
class DuplicateLessonView(LoginRequiredMixin, TeacherRequiredMixin, CreateView):
    model = Lesson
    form_class = LessonForm
    template_name = 'lessons/lesson_form.html'

    def get_source_lesson(self):
        if not hasattr(self, '_source_lesson'):
            self._source_lesson = get_object_or_404(
                Lesson.objects.select_related('class_group').prefetch_related(
                    'tags',
                    'exercises',
                ),
                pk=self.kwargs['pk'],
                class_group__teacher=self.request.user.teacher_profile,
            )

        return self._source_lesson

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['teacher'] = self.request.user.teacher_profile
        return kwargs

    def get_initial(self):
        source_lesson = self.get_source_lesson()

        return {
            'title': f'Cópia de {source_lesson.title}',
            'content': source_lesson.content,
            'performance_notes': '',
            'exercises': list(source_lesson.exercises.values_list('pk', flat=True)),
            'tags': list(source_lesson.tags.values_list('pk', flat=True)),
            'submission_status': Lesson.Status.PLANNED,
        }

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['is_duplicate'] = True
        context['duplicate_source'] = self.get_source_lesson()
        return context

    @transaction.atomic
    def form_valid(self, form):
        response = super().form_valid(form)

        messages.success(
            self.request,
            'Aula criada a partir da original. A turma, a data e os estados de aplicação foram definidos para esta nova aula.',
        )

        return response

    def get_success_url(self):
        return reverse('lesson_detail', kwargs={'pk': self.object.pk})
    
# Exercise Views
@method_decorator(csrf_protect, name='dispatch')
class ExerciseCreateView(LoginRequiredMixin, TeacherRequiredMixin, CreateView):
    model = Exercise
    form_class = ExerciseForm
    template_name = 'exercises/exercise_form.html'

    def get_source_lesson(self):
        if hasattr(self, '_source_lesson'):
            return self._source_lesson

        lesson_id = self.request.GET.get('lesson', '').strip()

        if not lesson_id:
            self._source_lesson = None
            return None

        if not lesson_id.isdigit():
            raise Http404('Aula não encontrada.')

        self._source_lesson = get_object_or_404(
            Lesson.objects.select_related('class_group'),
            pk=lesson_id,
            class_group__teacher=self.request.user.teacher_profile,
        )

        return self._source_lesson

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['teacher'] = self.request.user.teacher_profile
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['source_lesson'] = self.get_source_lesson()
        context['is_lesson_context'] = context['source_lesson'] is not None
        return context

    @transaction.atomic
    def form_valid(self, form):
        source_lesson = self.get_source_lesson()
        form.instance.created_by = self.request.user.teacher_profile

        if source_lesson:
            form.instance.is_template = False

        response = super().form_valid(form)

        if source_lesson:
            LessonExercise.objects.get_or_create(
                lesson=source_lesson,
                exercise=self.object,
                defaults={'is_applied': False},
            )

            messages.success(
                self.request,
                'Exercício criado e adicionado à aula com sucesso.',
            )
        else:
            messages.success(
                self.request,
                'Exercício criado com sucesso.',
            )

        return response

    def get_success_url(self):
        source_lesson = self.get_source_lesson()

        if source_lesson:
            return reverse(
                'lesson_detail',
                kwargs={'pk': source_lesson.pk},
            )

        return reverse('exercise_list')
    
@method_decorator(csrf_protect, name='dispatch')
class ExerciseListView(LoginRequiredMixin, TeacherRequiredMixin, ListView):
    model = Exercise
    template_name = 'exercises/exercise_list.html'
    context_object_name = 'exercises'
    paginate_by = 18

    def get_selected_status(self):
        status = self.request.GET.get('status', 'active')

        if status not in {'active', 'archived', 'all'}:
            status = 'active'

        return status

    def get_selected_type(self):
        exercise_type = self.request.GET.get('type', 'all')

        if exercise_type not in {'exercise', 'template', 'all'}:
            exercise_type = 'all'

        return exercise_type

    def get_selected_duration(self):
        duration = self.request.GET.get('duration', '')

        valid_durations = {
            '',
            'up-to-15',
            '16-to-30',
            '31-to-60',
            '61-to-120',
            'over-120',
            'without-duration',
        }

        return duration if duration in valid_durations else ''

    def get_queryset(self):
        queryset = Exercise.objects.filter(
            created_by=self.request.user.teacher_profile
        ).select_related(
            'created_by'
        ).prefetch_related(
            'tags',
            'objectives',
        )

        status = self.get_selected_status()
        exercise_type = self.get_selected_type()
        duration = self.get_selected_duration()

        search = self.request.GET.get('search', '').strip()
        tag_ids = [
            tag_id for tag_id in self.request.GET.getlist('tag') if tag_id.isdigit()
        ]

        objective_ids = [
            objective_id for objective_id in self.request.GET.getlist('objective') if objective_id.isdigit()
        ]

        if status == 'active':
            queryset = queryset.filter(is_active=True)
        elif status == 'archived':
            queryset = queryset.filter(is_active=False)

        if exercise_type == 'exercise':
            queryset = queryset.filter(is_template=False)
        elif exercise_type == 'template':
            queryset = queryset.filter(is_template=True)

        if search:
            queryset = queryset.filter(
                Q(title__icontains=search) |
                Q(description__icontains=search) |
                Q(materials__icontains=search)
            )

        if duration == 'up-to-15':
            queryset = queryset.filter(
                duration__gte=1,
                duration__lte=15,
            )
        elif duration == '16-to-30':
            queryset = queryset.filter(
                duration__gte=16,
                duration__lte=30,
            )
        elif duration == '31-to-60':
            queryset = queryset.filter(
                duration__gte=31,
                duration__lte=60,
            )
        elif duration == '61-to-120':
            queryset = queryset.filter(
                duration__gte=61,
                duration__lte=120,
            )
        elif duration == 'over-120':
            queryset = queryset.filter(duration__gt=120)
        elif duration == 'without-duration':
            queryset = queryset.filter(duration__isnull=True)

        if tag_ids:
            queryset = queryset.filter(
                tags__id__in=tag_ids
            )

        if objective_ids:
            queryset = queryset.filter(
                objectives__id__in=objective_ids
            )

        return queryset.distinct().order_by('title', 'id')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        teacher = self.request.user.teacher_profile

        base_exercises = Exercise.objects.filter(created_by=teacher)

        query_parameters = self.request.GET.copy()
        query_parameters.pop('page', None)

        context['search'] = self.request.GET.get('search', '').strip()
        context['selected_status'] = self.get_selected_status()
        context['selected_type'] = self.get_selected_type()
        context['selected_duration'] = self.get_selected_duration()
        context['selected_tags'] = [
            tag_id
            for tag_id in self.request.GET.getlist('tag')
            if tag_id.isdigit()
        ]

        context['selected_objectives'] = [
            objective_id
            for objective_id in self.request.GET.getlist('objective')
            if objective_id.isdigit()
        ]

        context['tags'] = Tag.objects.filter(
            teacher=teacher,
            type__in=['exercise', 'general'],
        ).order_by('name')

        context['objectives'] = LearningObjective.objects.filter(
            teacher=teacher
        ).order_by('title')

        context['has_any_exercises'] = base_exercises.exists()
        context['has_active_exercises'] = base_exercises.filter(
            is_active=True
        ).exists()
        context['has_archived_exercises'] = base_exercises.filter(
            is_active=False
        ).exists()
        context['has_templates'] = base_exercises.filter(
            is_template=True
        ).exists()
        context['has_regular_exercises'] = base_exercises.filter(
            is_template=False
        ).exists()

        context['query_string'] = query_parameters.urlencode()

        if context.get('paginator'):
            context['results_count'] = context['paginator'].count
        else:
            context['results_count'] = len(context['exercises'])

        return context
        
@method_decorator(csrf_protect, name='dispatch')
class ExerciseDetailView(LoginRequiredMixin, TeacherRequiredMixin, DetailView,):
    model = Exercise
    template_name = 'exercises/exercise_detail.html'
    context_object_name = 'exercise'

    def get_queryset(self):
        return Exercise.objects.filter(
            created_by=self.request.user.teacher_profile
        ).select_related(
            'created_by__user',
            'source_template',
        ).prefetch_related(
            'tags',
            'objectives',
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        related_lessons = self.object.lessons.select_related(
            'class_group'
        ).order_by(
            '-date',
            '-id',
        )

        lessons_count = related_lessons.count()

        generated_exercises = Exercise.objects.none()
        generated_exercises_count = 0

        if self.object.is_template:
            generated_exercises = (
                self.object.generated_exercises.order_by(
                    'title',
                    'id',
                )
            )

            generated_exercises_count = (
                generated_exercises.count()
            )

        context['related_lessons'] = related_lessons
        context['lessons_count'] = lessons_count

        context['generated_exercises'] = generated_exercises
        context['generated_exercises_count'] = (
            generated_exercises_count
        )

        context['can_delete_exercise'] = (
            lessons_count == 0
            and generated_exercises_count == 0
        )

        return context
        
@method_decorator(csrf_protect, name='dispatch')
class UseExerciseTemplateView(LoginRequiredMixin, TeacherRequiredMixin, View):
    @transaction.atomic
    def post(self, request, pk):
        exercise_template = get_object_or_404(
            Exercise,
            pk=pk,
            created_by=request.user.teacher_profile,
            is_template=True,
            is_active=True,
        )

        new_exercise = Exercise.objects.create(
            title=exercise_template.title,
            description=exercise_template.description,
            duration=exercise_template.duration,
            materials=exercise_template.materials,
            created_by=request.user.teacher_profile,
            is_template=False,
            source_template=exercise_template,
        )

        new_exercise.objectives.set(exercise_template.objectives.all())
        new_exercise.tags.set(exercise_template.tags.all())

        messages.success(
            request,
            'Exercício criado a partir do modelo. Revise os dados antes de utilizá-lo.',
        )

        return redirect('exercise_form', pk=new_exercise.pk)
        
@method_decorator(csrf_protect, name='dispatch')
class ExerciseUpdateView(LoginRequiredMixin, TeacherRequiredMixin, UpdateView):
    model = Exercise
    form_class = ExerciseForm
    template_name = 'exercises/exercise_form.html'
    
    def get_queryset(self):
        return Exercise.objects.filter(
            created_by=self.request.user.teacher_profile
        )
       
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['teacher'] = self.request.user.teacher_profile
        return kwargs
    
    def get_success_url(self):
        messages.success(self.request, "Exercício atualizado com sucesso!")
        return reverse('exercise_detail', kwargs={'pk': self.object.pk})
    
@method_decorator(csrf_protect, name='dispatch')
class ExerciseArchiveView(
    LoginRequiredMixin,
    TeacherRequiredMixin,
    View,
):
    def post(self, request, pk):
        exercise = get_object_or_404(
            Exercise,
            pk=pk,
            created_by=request.user.teacher_profile,
        )

        if not exercise.is_active:
            messages.info(
                request,
                'Este exercício já está arquivado.'
            )
            return redirect('exercise_detail', pk=exercise.pk)

        exercise.is_active = False
        exercise.save(update_fields=['is_active'])

        messages.success(
            request,
            (
                'Exercício arquivado com sucesso. '
                'Ele não aparecerá para uso em novas aulas, '
                'mas continuará preservado nas aulas anteriores.'
            )
        )

        return redirect('exercise_detail', pk=exercise.pk)


@method_decorator(csrf_protect, name='dispatch')
class ExerciseRestoreView(
    LoginRequiredMixin,
    TeacherRequiredMixin,
    View,
):
    def post(self, request, pk):
        exercise = get_object_or_404(
            Exercise,
            pk=pk,
            created_by=request.user.teacher_profile,
        )

        if exercise.is_active:
            messages.info(
                request,
                'Este exercício já está ativo.'
            )
            return redirect('exercise_detail', pk=exercise.pk)

        exercise.is_active = True
        exercise.save(update_fields=['is_active'])

        messages.success(
            request,
            'Exercício reativado com sucesso.'
        )

        return redirect('exercise_detail', pk=exercise.pk)

@method_decorator(csrf_protect, name='dispatch')
class ExerciseDeleteView(LoginRequiredMixin, TeacherRequiredMixin, DeleteView):
    model = Exercise
    success_url = reverse_lazy('exercise_list')
    http_method_names = ['post']
    
    def get_queryset(self):
        return Exercise.objects.filter(
            created_by=self.request.user.teacher_profile
        )

    def form_valid(self, form):
        lessons_count = self.object.lessons.count()

        generated_exercises_count = (
            self.object.generated_exercises.count()
            if self.object.is_template
            else 0
        )

        if lessons_count > 0 or generated_exercises_count > 0:
            if (
                lessons_count > 0
                and generated_exercises_count > 0
            ):
                message = (
                    'Este recurso não pode ser excluído porque está '
                    f'vinculado a {lessons_count} '
                    f'{"aula" if lessons_count == 1 else "aulas"} '
                    f'e possui {generated_exercises_count} '
                    f'{"cópia gerada" if generated_exercises_count == 1 else "cópias geradas"}. '
                    'Você pode arquivá-lo para removê-lo da lista principal '
                    'sem perder o histórico.'
                )

            elif lessons_count > 0:
                message = (
                    'Este exercício não pode ser excluído porque está '
                    f'vinculado a {lessons_count} '
                    f'{"aula" if lessons_count == 1 else "aulas"}. '
                    'Você pode arquivá-lo para removê-lo da lista principal '
                    'sem perder o histórico.'
                )

            else:
                message = (
                    'Este modelo não pode ser excluído porque já gerou '
                    f'{generated_exercises_count} '
                    f'{"exercício" if generated_exercises_count == 1 else "exercícios"}. '
                    'Você pode arquivá-lo para removê-lo da lista principal '
                    'sem perder a referência de origem das cópias.'
                )

            messages.error(
                self.request,
                message,
            )

            return redirect(
                'exercise_detail',
                pk=self.object.pk,
            )

        messages.success(
            self.request,
            'Exercício excluído com sucesso.'
        )

        return super().form_valid(form)
    
    
@require_POST
@csrf_protect
@login_required
def toggle_exercise_applied(request, lesson_id, exercise_id):
    """
    Atualiza o estado de aplicação de um exercício já vinculado à aula.
    """
    try:
        teacher = request.user.teacher_profile
    except AttributeError:
        return JsonResponse({
            'success': False,
            'message': 'Perfil de professor não encontrado.',
        }, status=403)

    lesson_exercise = get_object_or_404(
        LessonExercise.objects.select_related('lesson', 'exercise'),
        lesson_id=lesson_id,
        exercise_id=exercise_id,
        lesson__class_group__teacher=teacher,
    )

    try:
        data = json.loads(request.body.decode('utf-8'))
    except (json.JSONDecodeError, UnicodeDecodeError):
        return JsonResponse({
            'success': False,
            'message': 'Dados da requisição inválidos.',
        }, status=400)

    is_applied = data.get('is_applied')

    if not isinstance(is_applied, bool):
        return JsonResponse({
            'success': False,
            'message': 'O estado de aplicação deve ser verdadeiro ou falso.',
        }, status=400)

    if lesson_exercise.is_applied != is_applied:
        lesson_exercise.is_applied = is_applied
        lesson_exercise.save(update_fields=['is_applied', 'updated_at'])

    applied_count = LessonExercise.objects.filter(
        lesson_id=lesson_id,
        is_applied=True,
    ).count()

    total_count = LessonExercise.objects.filter(
        lesson_id=lesson_id,
    ).count()

    percentage = round(
        (applied_count / total_count) * 100
    ) if total_count else 0

    return JsonResponse({
        'success': True,
        'is_applied': lesson_exercise.is_applied,
        'applied_count': applied_count,
        'total_count': total_count,
        'percentage': percentage,
        'message': (
            'Exercício marcado como aplicado.'
            if lesson_exercise.is_applied
            else 'Exercício marcado como não aplicado.'
        ),
    })
    
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
    form_class = LearningObjectiveForm
    template_name = 'library/objective_form.html'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['teacher'] = self.request.user.teacher_profile
        return kwargs

    def form_valid(self, form):
        form.instance.teacher = self.request.user.teacher_profile
        messages.success(self.request, 'Objetivo de aprendizagem criado com sucesso.')
        return super().form_valid(form)

    def get_success_url(self):
        return f"{reverse('library')}?section=objectives"

@method_decorator(csrf_protect, name='dispatch')
class LearningObjectiveUpdateView(LoginRequiredMixin, TeacherRequiredMixin, UpdateView):
    model = LearningObjective
    form_class = LearningObjectiveForm
    template_name = 'library/objective_form.html'

    def get_queryset(self):
        return LearningObjective.objects.filter(
            teacher=self.request.user.teacher_profile
        )

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['teacher'] = self.request.user.teacher_profile
        return kwargs

    def form_valid(self, form):
        messages.success(
            self.request,
            'Objetivo de aprendizagem atualizado com sucesso.',
        )
        return super().form_valid(form)

    def get_success_url(self):
        return f"{reverse('library')}?section=objectives"
    
@method_decorator(csrf_protect, name='dispatch')
class LearningObjectiveArchiveView(LoginRequiredMixin, TeacherRequiredMixin, View):
    def post(self, request, pk):
        objective = get_object_or_404(
            LearningObjective,
            pk=pk,
            teacher=request.user.teacher_profile,
        )

        if not objective.is_active:
            messages.info(request, 'Este objetivo já está arquivado.')
        else:
            objective.is_active = False
            objective.save(update_fields=['is_active'])
            messages.success(
                request,
                'Objetivo arquivado. Ele continuará preservado nos exercícios anteriores.',
            )

        return redirect(f"{reverse('library')}?section=objectives&status=archived")


@method_decorator(csrf_protect, name='dispatch')
class LearningObjectiveRestoreView(LoginRequiredMixin, TeacherRequiredMixin, View):
    def post(self, request, pk):
        objective = get_object_or_404(
            LearningObjective,
            pk=pk,
            teacher=request.user.teacher_profile,
        )

        if objective.is_active:
            messages.info(request, 'Este objetivo já está ativo.')
        else:
            objective.is_active = True
            objective.save(update_fields=['is_active'])
            messages.success(request, 'Objetivo reativado com sucesso.')

        return redirect(f"{reverse('library')}?section=objectives")


@method_decorator(csrf_protect, name='dispatch')
class LearningObjectiveDeleteView(LoginRequiredMixin, TeacherRequiredMixin, View):
    @transaction.atomic
    def post(self, request, pk):
        objective = get_object_or_404(
            LearningObjective.objects.prefetch_related('exercises'),
            pk=pk,
            teacher=request.user.teacher_profile,
        )

        exercise_count = objective.exercises.count()

        if exercise_count:
            messages.error(
                request,
                (
                    'Este objetivo não pode ser excluído porque está vinculado '
                    f'a {exercise_count} '
                    f'{"exercício" if exercise_count == 1 else "exercícios"}. '
                    'Arquive-o para removê-lo dos novos cadastros sem perder o histórico.'
                ),
            )
        else:
            objective.delete()
            messages.success(
                request,
                'Objetivo de aprendizagem excluído com sucesso.',
            )

        return redirect(f"{reverse('library')}?section=objectives")
    
@method_decorator(csrf_protect, name='dispatch')
class QuickCreateLearningObjectiveView(LoginRequiredMixin, TeacherRequiredMixin, View):
    def post(self, request):
        try:
            data = json.loads(request.body) if request.content_type == 'application/json' else request.POST
        except json.JSONDecodeError:
            return JsonResponse({
                'success': False,
                'error': 'Dados inválidos.',
            }, status=400)

        title = data.get('title', '').strip()
        description = data.get('description', '').strip()

        if not title:
            return JsonResponse({
                'success': False,
                'error': 'Informe o título do objetivo.',
            }, status=400)

        if len(title) > LearningObjective._meta.get_field('title').max_length:
            return JsonResponse({
                'success': False,
                'error': 'O título deve possuir no máximo 200 caracteres.',
            }, status=400)

        existing_objective = LearningObjective.objects.filter(
            teacher=request.user.teacher_profile,
            title__iexact=title,
        ).first()

        if existing_objective and not existing_objective.is_active:
            return JsonResponse({
                'success': False,
                'error': (
                    'Já existe um objetivo arquivado com este título. '
                    'Reative-o pela Biblioteca para utilizá-lo novamente.'
                ),
            }, status=409)

        if existing_objective:
            return JsonResponse({
                'success': True,
                'created': False,
                'message': 'Este objetivo já estava cadastrado e foi selecionado.',
                'item': {
                    'id': existing_objective.id,
                    'title': existing_objective.title,
                    'description': existing_objective.description,
                },
            })

        objective = LearningObjective.objects.create(
            teacher=request.user.teacher_profile,
            title=title,
            description=description,
        )

        return JsonResponse({
            'success': True,
            'created': True,
            'message': 'Objetivo de aprendizagem criado e selecionado.',
            'item': {
                'id': objective.id,
                'title': objective.title,
                'description': objective.description,
            },
        }, status=201)
    
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
    

# Student Views
@method_decorator(csrf_protect, name='dispatch')
class StudentListView(LoginRequiredMixin, TeacherRequiredMixin, ListView):
    model = Student
    template_name = 'students/student_list.html'
    context_object_name = 'students'
    paginate_by = 20

    def dispatch(self, request, *args, **kwargs):
        self.class_group = None
        class_group_id = self.kwargs.get('class_group_id')

        if class_group_id:
            self.class_group = get_object_or_404(
                ClassGroup,
                pk=class_group_id,
                teacher=request.user.teacher_profile
            )

        return super().dispatch(request, *args, **kwargs)

    def get_selected_status(self):
        status = self.request.GET.get('status', 'active')

        if status not in {'active', 'inactive', 'all'}:
            status = 'active'

        return status

    def get_selected_class_group(self):
        if self.class_group:
            return str(self.class_group.pk)

        class_group_id = self.request.GET.get('class_group', '')
        return class_group_id if class_group_id.isdigit() else ''

    def get_queryset(self):
        queryset = Student.objects.filter(
            class_group__teacher=self.request.user.teacher_profile
        ).select_related('class_group')

        if self.class_group:
            queryset = queryset.filter(class_group=self.class_group)
        else:
            selected_class_group = self.get_selected_class_group()

            if selected_class_group:
                queryset = queryset.filter(class_group_id=selected_class_group)

        status = self.get_selected_status()
        search = self.request.GET.get('search', '').strip()

        if status == 'active':
            queryset = queryset.filter(is_active=True)
        elif status == 'inactive':
            queryset = queryset.filter(is_active=False)

        if search:
            for term in search.split():
                queryset = queryset.filter(
                    Q(first_name__icontains=term) |
                    Q(last_name__icontains=term)
                )

        return queryset.order_by('first_name', 'last_name', 'id')

    def get_paginate_by(self, queryset):
        if self.class_group:
            return None

        return self.paginate_by

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        teacher = self.request.user.teacher_profile

        if self.class_group:
            base_students = Student.objects.filter(class_group=self.class_group)
        else:
            base_students = Student.objects.filter(class_group__teacher=teacher)

        query_parameters = self.request.GET.copy()
        query_parameters.pop('page', None)

        context['class_group'] = self.class_group
        context['is_class_group_scope'] = self.class_group is not None
        context['search'] = self.request.GET.get('search', '').strip()
        context['selected_status'] = self.get_selected_status()
        context['selected_class_group'] = self.get_selected_class_group()
        context['class_groups'] = ClassGroup.objects.filter(
            teacher=teacher
        ).order_by('-is_active', 'name', 'year')
        context['active_class_groups'] = ClassGroup.objects.filter(
            teacher=teacher,
            is_active=True
        ).order_by('name', 'year')
        context['query_string'] = query_parameters.urlencode()        
        context['has_any_students'] = base_students.exists()
        context['has_active_students'] = base_students.filter(is_active=True).exists()
        context['has_inactive_students'] = base_students.filter(is_active=False).exists()
        
        if context.get('paginator'):
            context['results_count'] = context['paginator'].count
        else:
            context['results_count'] = len(context['students'])        

        return context

@method_decorator(csrf_protect, name='dispatch')
class StudentDetailView(LoginRequiredMixin, TeacherRequiredMixin, DetailView):
    model = Student
    template_name = 'students/student_detail.html'
    context_object_name = 'student'
    
    def get_queryset(self):
        return Student.objects.filter(
            class_group_id=self.kwargs.get('class_group_id'),
            class_group__teacher=self.request.user.teacher_profile
        ).select_related('class_group')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        today = timezone.localdate()
        birth_date = self.object.birth_date

        if birth_date:
            age = today.year - birth_date.year
            birthday_has_not_occurred = (
                today.month,
                today.day,
            ) < (
                birth_date.month,
                birth_date.day,
            )

            if birthday_has_not_occurred:
                age -= 1

            context['student_age'] = age
        else:
            context['student_age'] = None

        return context

@method_decorator(csrf_protect, name='dispatch')
class StudentCreateView(LoginRequiredMixin, TeacherRequiredMixin, CreateView):
    model = Student
    form_class = StudentForm
    template_name = 'students/student_form.html'
    
    def dispatch(self, request, *args, **kwargs):
        # Verifica se a turma pertence a este professor
        self.class_group = get_object_or_404(
            ClassGroup, 
            pk=self.kwargs.get('class_group_id'),
            teacher=self.request.user.teacher_profile
        )
        return super().dispatch(request, *args, **kwargs)
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['class_group'] = self.class_group
        return kwargs
    
    def form_valid(self, form):
        form.instance.class_group = self.class_group
        self.object = form.save()

        messages.success(
            self.request,
            "Aluno cadastrado com sucesso! Você já pode cadastrar o próximo aluno."
        )

        return redirect(
            'student_form',
            class_group_id=self.class_group.pk
        )
    
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['class_group'] = self.class_group
        return context

@method_decorator(csrf_protect, name='dispatch')
class StudentUpdateView(LoginRequiredMixin, TeacherRequiredMixin, UpdateView):
    model = Student
    form_class = StudentForm
    template_name = 'students/student_form.html'

    def dispatch(self, request, *args, **kwargs):
        self.class_group = get_object_or_404(
            ClassGroup,
            pk=self.kwargs.get('class_group_id'),
            teacher=self.request.user.teacher_profile
        )
        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        return Student.objects.filter(class_group=self.class_group)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['class_group'] = self.class_group
        return context

    def form_valid(self, form):
        form.instance.class_group = self.class_group

        messages.success(
            self.request,
            "Dados do aluno atualizados com sucesso."
        )

        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse(
            'student_detail',
            kwargs={
                'class_group_id': self.class_group.pk,
                'pk': self.object.pk,
            }
        )    


@method_decorator(csrf_protect, name='dispatch')
class StudentDeleteView(LoginRequiredMixin, TeacherRequiredMixin, DeleteView):
    model = Student

    def get_queryset(self):
        return Student.objects.filter(
            class_group_id=self.kwargs.get('class_group_id'),
            class_group__teacher=self.request.user.teacher_profile
        )

    def form_valid(self, form):
        class_group_id = self.object.class_group_id

        messages.success(
            self.request,
            'Aluno excluído com sucesso.'
        )

        self.object.delete()

        return redirect(
            'class_group_students',
            class_group_id=class_group_id
        )
 
@method_decorator(csrf_protect, name='dispatch')
class LibraryView(LoginRequiredMixin, TeacherRequiredMixin, TemplateView):
    template_name = 'library/library_list.html'

    VALID_SECTIONS = {'objectives', 'tags'}
    VALID_STATUSES = {'active', 'archived', 'all'}
    VALID_TAG_TYPES = {'lesson', 'exercise', 'general'}

    def get_selected_section(self):
        section = self.request.GET.get('section', 'objectives')
        return section if section in self.VALID_SECTIONS else 'objectives'

    def get_selected_status(self):
        status = self.request.GET.get('status', 'active')
        return status if status in self.VALID_STATUSES else 'active'

    def get_search_query(self):
        return ' '.join(self.request.GET.get('q', '').split())[:100]

    def get_selected_tag_type(self):
        tag_type = self.request.GET.get('type', '')
        return tag_type if tag_type in self.VALID_TAG_TYPES else ''

    def apply_status_filter(self, queryset):
        status = self.get_selected_status()

        if status == 'active':
            return queryset.filter(is_active=True)

        if status == 'archived':
            return queryset.filter(is_active=False)

        return queryset

    def get_objectives(self, teacher):
        queryset = LearningObjective.objects.filter(
            teacher=teacher
        ).annotate(
            exercise_count=Count('exercises', distinct=True),
        )

        search_query = self.get_search_query()

        if search_query:
            queryset = queryset.filter(
                Q(title__icontains=search_query)
                | Q(description__icontains=search_query)
            )

        return self.apply_status_filter(queryset).order_by('title')

    def get_tags(self, teacher):
        queryset = Tag.objects.filter(
            teacher=teacher
        ).annotate(
            lesson_count=Count('lessons', distinct=True),
            exercise_count=Count('exercises', distinct=True),
        )

        search_query = self.get_search_query()
        selected_type = self.get_selected_tag_type()

        if search_query:
            queryset = queryset.filter(name__icontains=search_query)

        if selected_type:
            queryset = queryset.filter(type=selected_type)

        return self.apply_status_filter(queryset).order_by('name')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        teacher = self.request.user.teacher_profile
        selected_section = self.get_selected_section()

        objective_base = LearningObjective.objects.filter(teacher=teacher)
        tag_base = Tag.objects.filter(teacher=teacher)

        context['selected_section'] = selected_section
        context['selected_status'] = self.get_selected_status()
        context['selected_tag_type'] = self.get_selected_tag_type()
        context['search_query'] = self.get_search_query()
        context['tag_type_choices'] = Tag.TYPE_CHOICES

        context['objective_active_count'] = objective_base.filter(is_active=True).count()
        context['objective_archived_count'] = objective_base.filter(is_active=False).count()
        context['tag_active_count'] = tag_base.filter(is_active=True).count()
        context['tag_archived_count'] = tag_base.filter(is_active=False).count()

        context['objectives'] = self.get_objectives(teacher) if selected_section == 'objectives' else LearningObjective.objects.none()
        context['tags'] = self.get_tags(teacher) if selected_section == 'tags' else Tag.objects.none()

        return context
 
@method_decorator(csrf_protect, name='dispatch')
class TagCreateView(LoginRequiredMixin, TeacherRequiredMixin, CreateView):
    model = Tag
    form_class = TagForm
    template_name = 'library/tag_form.html'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['teacher'] = self.request.user.teacher_profile
        return kwargs

    def form_valid(self, form):
        form.instance.teacher = self.request.user.teacher_profile
        messages.success(self.request, 'Tag criada com sucesso.')
        return super().form_valid(form)

    def get_success_url(self):
        return f"{reverse('library')}?section=tags"


@method_decorator(csrf_protect, name='dispatch')
class TagUpdateView(LoginRequiredMixin, TeacherRequiredMixin, UpdateView):
    model = Tag
    form_class = TagForm
    template_name = 'library/tag_form.html'

    def get_queryset(self):
        return Tag.objects.filter(
            teacher=self.request.user.teacher_profile
        )

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['teacher'] = self.request.user.teacher_profile
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['lesson_count'] = self.object.lessons.count()
        context['exercise_count'] = self.object.exercises.count()
        return context

    def form_valid(self, form):
        messages.success(self.request, 'Tag atualizada com sucesso.')
        return super().form_valid(form)

    def get_success_url(self):
        return f"{reverse('library')}?section=tags"
    
@method_decorator(csrf_protect, name='dispatch')
class TagArchiveView(LoginRequiredMixin, TeacherRequiredMixin, View):
    def post(self, request, pk):
        tag = get_object_or_404(
            Tag,
            pk=pk,
            teacher=request.user.teacher_profile,
        )

        if not tag.is_active:
            messages.info(request, 'Esta tag já está arquivada.')
        else:
            tag.is_active = False
            tag.save(update_fields=['is_active'])
            messages.success(
                request,
                'Tag arquivada. Ela continuará preservada nos registros anteriores.',
            )

        return redirect(f"{reverse('library')}?section=tags&status=archived")


@method_decorator(csrf_protect, name='dispatch')
class TagRestoreView(LoginRequiredMixin, TeacherRequiredMixin, View):
    def post(self, request, pk):
        tag = get_object_or_404(
            Tag,
            pk=pk,
            teacher=request.user.teacher_profile,
        )

        if tag.is_active:
            messages.info(request, 'Esta tag já está ativa.')
        else:
            tag.is_active = True
            tag.save(update_fields=['is_active'])
            messages.success(request, 'Tag reativada com sucesso.')

        return redirect(f"{reverse('library')}?section=tags")


@method_decorator(csrf_protect, name='dispatch')
class TagDeleteView(LoginRequiredMixin, TeacherRequiredMixin, View):
    @transaction.atomic
    def post(self, request, pk):
        tag = get_object_or_404(
            Tag,
            pk=pk,
            teacher=request.user.teacher_profile,
        )

        lesson_count = tag.lessons.count()
        exercise_count = tag.exercises.count()
        total_links = lesson_count + exercise_count

        if total_links:
            links = []

            if lesson_count:
                links.append(
                    f'{lesson_count} {"aula" if lesson_count == 1 else "aulas"}'
                )

            if exercise_count:
                links.append(
                    f'{exercise_count} '
                    f'{"exercício" if exercise_count == 1 else "exercícios"}'
                )

            messages.error(
                request,
                (
                    'Esta tag não pode ser excluída porque está vinculada a '
                    f'{", ".join(links)}. Arquive-a para preservar o histórico.'
                ),
            )
        else:
            tag.delete()
            messages.success(request, 'Tag excluída com sucesso.')

        return redirect(f"{reverse('library')}?section=tags")
    
@method_decorator(csrf_protect, name='dispatch')
class QuickCreateExerciseTagView(LoginRequiredMixin, TeacherRequiredMixin, View):
    def post(self, request):
        try:
            data = json.loads(request.body) if request.content_type == 'application/json' else request.POST
        except json.JSONDecodeError:
            return JsonResponse({
                'success': False,
                'error': 'Dados inválidos.',
            }, status=400)

        tag_name = data.get('name', '').strip()

        if not tag_name:
            return JsonResponse({
                'success': False,
                'error': 'Informe o nome da tag.',
            }, status=400)

        if len(tag_name) > Tag._meta.get_field('name').max_length:
            return JsonResponse({
                'success': False,
                'error': 'O nome da tag deve possuir no máximo 50 caracteres.',
            }, status=400)

        if not re.match(r'^[\w\sÀ-ÿ\-]+$', tag_name):
            return JsonResponse({
                'success': False,
                'error': 'Use apenas letras, números, espaços, hífens e underscores.',
            }, status=400)

        existing_tag = Tag.objects.filter(
            teacher=request.user.teacher_profile,
            name__iexact=tag_name,
            type__in=['exercise', 'general'],
        ).order_by('type', 'id').first()

        if existing_tag and not existing_tag.is_active:
            return JsonResponse({
                'success': False,
                'error': (
                    'Já existe uma tag arquivada com este nome. '
                    'Reative-a pela Biblioteca para utilizá-la novamente.'
                ),
            }, status=409)

        if existing_tag:
            return JsonResponse({
                'success': True,
                'created': False,
                'message': 'Esta tag já estava cadastrada e foi selecionada.',
                'item': {
                    'id': existing_tag.id,
                    'name': existing_tag.name,
                    'color': existing_tag.color,
                },
            })

        tag = Tag.objects.create(
            teacher=request.user.teacher_profile,
            name=tag_name,
            type='exercise',
            color=Tag.generate_random_color(),
        )

        return JsonResponse({
            'success': True,
            'created': True,
            'message': 'Tag criada e selecionada.',
            'item': {
                'id': tag.id,
                'name': tag.name,
                'color': tag.color,
            },
        }, status=201)

@method_decorator(csrf_exempt, name='dispatch')
class CheckTagAPIView(LoginRequiredMixin, View):
    """
    API endpoint para verificar se uma tag já existe
    """
    
    def get(self, request):
        try:
            tag_name = request.GET.get('name', '').strip().lower()
            
            if not tag_name:
                return JsonResponse({
                    'exists': False,
                    'error': 'Nome da tag não fornecido'
                }, status=400)
            
            # Verifica se a tag já existe para este professor
            tag_exists = Tag.objects.filter(
                name__iexact=tag_name,
                teacher=request.user.teacher_profile
            ).exists()
            
            return JsonResponse({
                'exists': tag_exists,
                'tag_name': tag_name
            })
            
        except AttributeError:
            # Usuário não tem teacher_profile
            return JsonResponse({
                'exists': False,
                'error': 'Perfil de professor não encontrado'
            }, status=403)
            
        except Exception as e:
            return JsonResponse({
                'exists': False,
                'error': f'Erro interno: {str(e)}'
            }, status=500)

@method_decorator(csrf_protect, name='dispatch')
class QuickAddTagView(
    LoginRequiredMixin,
    TeacherRequiredMixin,
    View,
):
    ALLOWED_MODEL_TYPES = {
        'lesson',
        'exercise',
    }

    @transaction.atomic
    def post(self, request, model_type=None, model_id=None):
        if model_type not in self.ALLOWED_MODEL_TYPES:
            return JsonResponse(
                {
                    'success': False,
                    'error': 'Tipo de recurso inválido.',
                },
                status=400,
            )

        tag_name = self.get_tag_name(request)

        validation_error = self.validate_tag_name(tag_name)

        if validation_error:
            return JsonResponse(
                {
                    'success': False,
                    'error': validation_error,
                },
                status=400,
            )

        teacher = request.user.teacher_profile

        target_object = self.get_target_object(
            model_type=model_type,
            model_id=model_id,
            teacher=teacher,
        )

        if target_object is None:
            return JsonResponse(
                {
                    'success': False,
                    'error': 'Recurso não encontrado.',
                },
                status=404,
            )

        tag = Tag.objects.filter(
            teacher=teacher,
            name__iexact=tag_name,
            type__in=[
                model_type,
                'general',
            ],
            is_active=True,
        ).order_by(
            'type',
            'id',
        ).first()

        created = False
        
        archived_tag_exists = Tag.objects.filter(
            teacher=teacher,
            name__iexact=tag_name,
            type__in=[model_type, 'general'],
            is_active=False,
        ).exists()

        if tag is None and archived_tag_exists:
            return JsonResponse(
                {
                    'success': False,
                    'error': (
                        'Já existe uma tag arquivada com este nome. '
                        'Reative-a pela Biblioteca para utilizá-la novamente.'
                    ),
                },
                status=409,
            )        

        if tag is None:
            tag = Tag.objects.create(
                name=tag_name,
                teacher=teacher,
                type=model_type,
                color=Tag.generate_random_color(),
            )

            created = True

        target_object.tags.add(tag)

        if not target_object.tags.filter(pk=tag.pk).exists():
            transaction.set_rollback(True)

            return JsonResponse(
                {
                    'success': False,
                    'error': 'Não foi possível associar a tag ao recurso.',
                },
                status=500,
            )

        if created:
            message = (
                f'Tag "{tag.name}" criada e adicionada com sucesso.'
            )
        else:
            message = (
                f'Tag "{tag.name}" associada com sucesso.'
            )

        return JsonResponse(
            {
                'success': True,
                'message': message,
                'tag': {
                    'id': tag.pk,
                    'name': tag.name,
                    'color': tag.color,
                    'type': tag.type,
                },
            },
            status=201 if created else 200,
        )

    def get_tag_name(self, request):
        content_type = request.content_type.split(';')[0]

        if content_type == 'application/json':
            try:
                data = json.loads(
                    request.body.decode('utf-8')
                )
            except (
                json.JSONDecodeError,
                UnicodeDecodeError,
            ):
                return ''

            raw_tag_name = data.get('tag_name', '')
        else:
            raw_tag_name = request.POST.get(
                'tag_name',
                ''
            )

        return ' '.join(
            str(raw_tag_name).split()
        )

    def validate_tag_name(self, tag_name):
        if not tag_name:
            return 'O nome da tag não pode estar vazio.'

        if len(tag_name) < 2:
            return (
                'O nome da tag deve ter pelo menos 2 caracteres.'
            )

        if len(tag_name) > 50:
            return (
                'O nome da tag não pode ultrapassar 50 caracteres.'
            )

        if not re.fullmatch(
            r'[\w\sÀ-ÿ\-]+',
            tag_name,
        ):
            return (
                'Use apenas letras, números, espaços, '
                'hífens e underscores.'
            )

        return None

    def get_target_object(
        self,
        model_type,
        model_id,
        teacher,
    ):
        if model_type == 'exercise':
            return Exercise.objects.filter(
                pk=model_id,
                created_by=teacher,
            ).first()

        if model_type == 'lesson':
            return Lesson.objects.filter(
                pk=model_id,
                class_group__teacher=teacher,
            ).first()

        return None