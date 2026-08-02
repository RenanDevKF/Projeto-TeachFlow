from django.template import context
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, View
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from django.urls import reverse_lazy, reverse
from django.shortcuts import redirect, get_object_or_404, render
from django.contrib import messages
from django.db import transaction
from django.db.models import Q, Case, IntegerField, Value, When
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_protect, csrf_exempt
from django.views.decorators.http import require_POST
from django.http import JsonResponse, Http404, HttpResponseRedirect
from datetime import date
from .models import ClassGroup, Student, Lesson, Exercise, Tag, LearningObjective, FutureIdea
from .forms import *
from django.utils import timezone
from datetime import date
from collections import defaultdict
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
    
# Lesson Views
@method_decorator(csrf_protect, name='dispatch')
class LessonListView(LoginRequiredMixin, TeacherRequiredMixin, ListView):
    model = Lesson
    template_name = 'lessons/lesson_list.html'
    context_object_name = 'lessons'
    paginate_by = 10

    def get_queryset(self):
        queryset = Lesson.objects.filter(
            class_group__teacher=self.request.user.teacher_profile
        ).select_related('class_group').prefetch_related('tags')
        
        # Filtros
        class_group_id = self.request.GET.get('class')
        tag_id = self.request.GET.get('tag')
        date_filter = self.request.GET.get('date')
        
        if class_group_id:
            queryset = queryset.filter(class_group_id=class_group_id)
        
        if tag_id:
            queryset = queryset.filter(tags__id=tag_id)
        
        if date_filter:
            queryset = queryset.filter(date=date_filter)
        
        return queryset.order_by('date', 'title')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        teacher = self.request.user.teacher_profile
        
        # Filtros para o template
        context['class_groups'] = ClassGroup.objects.filter(teacher=teacher)
        context['tags'] = Tag.objects.filter(teacher=teacher)
        
        # Separar aulas por data
        today = date.today()
        all_lessons = self.get_queryset()
        
        # Aulas futuras (ordenadas da mais próxima para a mais distante)
        future_lessons = all_lessons.filter(date__gte=today).order_by('date', 'title')
        
        # Aulas passadas (ordenadas da mais recente para a mais antiga)
        past_lessons = all_lessons.filter(date__lt=today).order_by('-date', 'title')
        
        context['future_lessons'] = future_lessons
        context['past_lessons'] = past_lessons
        context['today'] = today
        
        return context

# Suas outras views permanecem iguais...
@method_decorator(csrf_protect, name='dispatch')
class LessonDetailView(LoginRequiredMixin, TeacherRequiredMixin, OwnershipRequiredMixin, DetailView):
    model = Lesson
    template_name = 'lessons/lesson_detail.html'
    context_object_name = 'lesson'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Adicionar informações sobre exercícios aplicados
        applied_exercises_key = f'applied_exercises_lesson_{self.object.id}'
        applied_exercises = self.request.session.get(applied_exercises_key, [])
        context['applied_exercises'] = applied_exercises
        
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
        messages.success(self.request, "Aula criada com sucesso!")
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
    
    def get_success_url(self):
        return reverse_lazy('lesson-list', kwargs={'class_group_id': self.object.class_group_id})
    
@method_decorator(csrf_protect, name='dispatch')
class DuplicateLessonView(LoginRequiredMixin, TeacherRequiredMixin, View):
    def get(self, request, pk):
        original_lesson = get_object_or_404(
            Lesson, 
            pk=pk, 
            class_group__teacher=request.user.teacher_profile
        )
        
        new_lesson = Lesson.objects.create(
            title=f"Cópia de {original_lesson.title}",
            date=original_lesson.date,
            content=original_lesson.content,
            performance_notes=original_lesson.performance_notes,
            class_group=original_lesson.class_group,
        )
        
        # Copia relacionamentos ManyToMany
        new_lesson.tags.set(original_lesson.tags.all())
        new_lesson.objectives.set(original_lesson.objectives.all())
        
        # Copia exercícios (se necessário)
        for exercise in original_lesson.exercises.all():
            Exercise.objects.create(
                lesson=new_lesson,
                title=exercise.title,
                description=exercise.description,
                duration=exercise.duration,
                materials=exercise.materials
            )
        
        messages.success(request, "Aula duplicada com sucesso!")
        return redirect('lesson_update', pk=new_lesson.pk)
    
# Exercise Views
@method_decorator(csrf_protect, name='dispatch')
class ExerciseCreateView(LoginRequiredMixin, TeacherRequiredMixin, CreateView):
    model = Exercise
    form_class = ExerciseForm  # Usando o formulário personalizado
    template_name = 'exercises/exercise_form.html'
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['teacher'] = self.request.user.teacher_profile
        return kwargs
    
    def form_valid(self, form):
        form.instance.created_by = self.request.user.teacher_profile
        messages.success(self.request, "Exercício criado com sucesso!")
        return super().form_valid(form)
    
    def get_success_url(self):
        # Redireciona de volta à lista de exercícios
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
        tag_id = self.request.GET.get('tag', '')
        objective_id = self.request.GET.get('objective', '')

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

        if tag_id.isdigit():
            queryset = queryset.filter(tags__id=tag_id)

        if objective_id.isdigit():
            queryset = queryset.filter(objectives__id=objective_id)

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
        context['selected_tag'] = self.request.GET.get('tag', '')
        context['selected_objective'] = self.request.GET.get(
            'objective',
            ''
        )

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
class ExerciseDetailView(LoginRequiredMixin, TeacherRequiredMixin, DetailView):
    model = Exercise
    template_name = 'exercises/exercise_detail.html'
    context_object_name = 'exercise'

    def get_queryset(self):
        return Exercise.objects.filter(
            created_by=self.request.user.teacher_profile
        ).select_related(
            'created_by',
        ).prefetch_related(
            'tags',
            'objectives',
            'lessons__class_group',
        )
        
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

        if lessons_count > 0:
            messages.error(
                self.request,
                (
                    'Este exercício não pode ser excluído porque está vinculado '
                    f'a {lessons_count} '
                    f'{"aula" if lessons_count == 1 else "aulas"}. '
                    'Você pode arquivá-lo para removê-lo da lista principal.'
                )
            )

            return redirect(
                'exercise_detail',
                pk=self.object.pk
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
    Marca/desmarca um exercício como aplicado em uma aula específica
    """
    try:
        # Verificar se o professor tem acesso à aula
        lesson = get_object_or_404(
            Lesson, 
            pk=lesson_id, 
            class_group__teacher=request.user.teacher_profile
        )
        
        # Verificar se o exercício existe e está relacionado à aula
        exercise = get_object_or_404(Exercise, pk=exercise_id)
        
        # Verificar se o exercício já está na aula
        if exercise in lesson.exercises.all():
            # Se já está, verificar se está marcado como aplicado
            # Vamos usar um campo personalizado ou relacionamento
            # Primeiro, vamos verificar se existe um modelo intermediário
            
            # Como não há um modelo intermediário explícito, vamos usar
            # a abordagem de adicionar/remover da lista de exercícios aplicados
            
            # Vamos criar um campo separado para exercícios aplicados
            # Por enquanto, usando a abordagem com session ou cache
            
            applied_exercises_key = f'applied_exercises_lesson_{lesson_id}'
            applied_exercises = request.session.get(applied_exercises_key, [])
            
            if exercise_id in applied_exercises:
                applied_exercises.remove(exercise_id)
                is_applied = False
            else:
                applied_exercises.append(exercise_id)
                is_applied = True
                
            request.session[applied_exercises_key] = applied_exercises
            request.session.modified = True
            
            return JsonResponse({
                'success': True,
                'is_applied': is_applied,
                'message': 'Exercício marcado como aplicado' if is_applied else 'Exercício desmarcado'
            })
        else:
            return JsonResponse({
                'success': False,
                'message': 'Exercício não está relacionado a esta aula'
            })
            
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Erro ao processar solicitação: {str(e)}'
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
class TagCreateView(LoginRequiredMixin, CreateView):  # Removido TeacherRequiredMixin temporariamente
    model = Tag
    fields = ['name', 'type', 'color']
    template_name = 'core/tag_form.html'
    
    def form_valid(self, form):
        form.instance.teacher = self.request.user.teacher_profile
        messages.success(self.request, "Tag criada com sucesso!")
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse('tag_list')

@method_decorator(csrf_protect, name='dispatch')    
class TagListView(LoginRequiredMixin, ListView):  # Removido TeacherRequiredMixin temporariamente
    model = Tag
    template_name = 'tag/tag_list.html'
    context_object_name = 'tags'
    
    def get_queryset(self):
        # Filtra tags apenas do professor logado
        queryset = Tag.objects.filter(teacher=self.request.user.teacher_profile)
        
        # Filtro por tipo (opcional)
        tag_type = self.request.GET.get('type')
        if tag_type:
            queryset = queryset.filter(type=tag_type)
            
        return queryset.order_by('name')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Adiciona TYPE_CHOICES se existir no modelo
        if hasattr(Tag, 'TYPE_CHOICES'):
            context['type_choices'] = Tag.TYPE_CHOICES
        
        # Se não há filtro específico, organiza tags por categoria
        if not self.request.GET.get('type'):
            all_tags = Tag.objects.filter(
                teacher=self.request.user.teacher_profile
            ).order_by('name')
            
            # Organiza as tags por categoria
            tags_by_type = defaultdict(list)
            for tag in all_tags:
                tags_by_type[tag.type].append(tag)
            
            # Converte para dict normal
            context['tags_by_type'] = dict(tags_by_type)
        else:
            # Se há filtro, não precisamos organizar por categoria
            context['tags_by_type'] = {}
            
        return context

@method_decorator(csrf_protect, name='dispatch')
class TagUpdateView(LoginRequiredMixin, UpdateView):  # Removido TeacherRequiredMixin temporariamente
    model = Tag
    fields = ['name', 'type', 'color']
    template_name = 'core/tag_form.html'
    
    def get_queryset(self):
        return Tag.objects.filter(teacher=self.request.user.teacher_profile)
    
    def form_valid(self, form):
        messages.success(self.request, "Tag atualizada com sucesso!")
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse('tag_list')

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

# Versão melhorada da QuickAddTagView
@method_decorator(csrf_exempt, name='dispatch')
class QuickAddTagView(LoginRequiredMixin, View):
    def post(self, request, model_type=None, model_id=None):
        try:
            tag_name = ''

            # Compatível com form-data e JSON
            if request.method == 'POST':
                if request.content_type == 'application/json':
                    try:
                        data = json.loads(request.body)
                        tag_name = data.get('tag_name', '').strip()
                    except json.JSONDecodeError:
                        tag_name = ''
                else:
                    tag_name = request.POST.get('tag_name', '').strip()

            # Validações básicas
            if not tag_name:
                return JsonResponse({
                    'success': False,
                    'error': 'O nome da tag não pode estar vazio'
                }, status=400)

            if len(tag_name) < 2:
                return JsonResponse({
                    'success': False,
                    'error': 'O nome da tag deve ter pelo menos 2 caracteres'
                }, status=400)

            if not re.match(r'^[\w\sÀ-ÿ\-]+$', tag_name):
                return JsonResponse({
                    'success': False,
                    'error': 'Use apenas letras, números, espaços, hífens e underscores'
                }, status=400)

            # Verifica se a tag já existe (case-insensitive)
            existing_tag = Tag.objects.filter(
                name__iexact=tag_name,
                teacher=request.user.teacher_profile
            ).first()

            if existing_tag:
                tag = existing_tag
                created = False
            else:
                tag = Tag.objects.create(
                    name=tag_name,
                    teacher=request.user.teacher_profile,
                    type=model_type if model_type else 'general',
                    color=Tag.generate_random_color()
                )
                created = True

            # Associa a tag ao modelo
            model = self.get_model_instance(model_type, model_id)
            if model and hasattr(model, 'tags'):
                model.tags.add(tag)

            return JsonResponse({
                'success': True,
                'message': f'Tag "{tag_name}" {"criada e adicionada" if created else "já existia e foi associada"} com sucesso!',
                'tag': {
                    'id': tag.id,
                    'name': tag.name,
                    'color': tag.color
                }
            })

        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': f'Erro interno: {str(e)}'
            }, status=500)

    def get_model_instance(self, model_type, model_id):
        if not model_type or not model_id:
            return None

        try:
            if model_type == 'lesson':
                return Lesson.objects.get(
                    pk=model_id,
                    class_group__teacher=self.request.user.teacher_profile
                )
            elif model_type == 'exercise':
                return Exercise.objects.get(
                    pk=model_id,
                    lessons__class_group__teacher=self.request.user.teacher_profile
                )
        except (Lesson.DoesNotExist, Exercise.DoesNotExist):
            return None
