from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, View
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from django.urls import reverse_lazy, reverse
from django.shortcuts import redirect, get_object_or_404, render
from django.contrib import messages
from django.db.models import Q
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_protect
from django.http import JsonResponse, Http404, HttpResponseRedirect
from datetime import date
from .models import ClassGroup, Student, Lesson, Exercise, Tag, LearningObjective, FutureIdea
from .forms import *
from django.utils import timezone
from datetime import date

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
    
    def get_queryset(self):
        queryset = ClassGroup.objects.filter(
            teacher=self.request.user.teacher_profile
        ).prefetch_related('students', 'lessons')
        
        # Adicione os filtros aqui
        search = self.request.GET.get('search')
        school = self.request.GET.get('school')
        year = self.request.GET.get('year')
        period = self.request.GET.get('period')
        
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
            
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Adicione os valores atuais dos filtros ao contexto
        context['search'] = self.request.GET.get('search', '')
        context['school'] = self.request.GET.get('school', '')
        context['year'] = self.request.GET.get('year', '')
        context['period'] = self.request.GET.get('period', '')
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
class ClassGroupDeleteView(LoginRequiredMixin, TeacherRequiredMixin, OwnershipRequiredMixin, DeleteView):
    model = ClassGroup
    template_name = 'classes/class_group_confirm_delete.html'
    success_url = reverse_lazy('class_group_list')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['class_group'] = self.get_object()  # Garante que o objeto está no contexto
        return context
    
    def delete(self, request, *args, **kwargs):
        messages.success(request, "Class group deleted successfully.")
        return super().delete(request, *args, **kwargs)
    
# Lesson Views
@method_decorator(csrf_protect, name='dispatch')
class LessonListView(LoginRequiredMixin, TeacherRequiredMixin, ListView):
    model = Lesson
    template_name = 'lessons/lesson_list.html'  # Mantém o mesmo template
    context_object_name = 'lessons'
    paginate_by = 10  # Adicione paginação se desejar

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
        
        return queryset.order_by('-date', 'title')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        teacher = self.request.user.teacher_profile
        context['class_groups'] = ClassGroup.objects.filter(teacher=teacher)
        context['tags'] = Tag.objects.filter(teacher=teacher)
        return context

@method_decorator(csrf_protect, name='dispatch')
class LessonDetailView(LoginRequiredMixin, TeacherRequiredMixin, OwnershipRequiredMixin, DetailView):
    model = Lesson
    template_name = 'lessons/lesson_detail.html'
    context_object_name = 'lesson'


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
        if self.object:  # Para update view
            context['selected_tags'] = self.object.tags.values_list('id', flat=True)
        else:  # Para create view
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
        if self.object:  # Para update view
            context['selected_tags'] = self.object.tags.values_list('id', flat=True)
        else:  # Para create view
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
    
    def get_queryset(self):
        return Exercise.objects.filter(
        Q(created_by=self.request.user.teacher_profile) |
        Q(lessons__class_group__teacher=self.request.user.teacher_profile)
    ).distinct().select_related('created_by')
        
@method_decorator(csrf_protect, name='dispatch')
class ExerciseDetailView(LoginRequiredMixin, TeacherRequiredMixin, DetailView):
    model = Exercise
    template_name = 'exercises/exercise_detail.html'
    context_object_name = 'exercise'

    def get_queryset(self):
        # Filtra para mostrar apenas exercícios do professor
        return Exercise.objects.filter(
            Q(created_by=self.request.user.teacher_profile) |
            Q(lessons__class_group__teacher=self.request.user.teacher_profile)
        ).distinct()
        
@method_decorator(csrf_protect, name='dispatch')
class ExerciseUpdateView(LoginRequiredMixin, TeacherRequiredMixin, UpdateView):
    model = Exercise
    form_class = ExerciseForm
    template_name = 'exercises/exercise_form.html'
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['teacher'] = self.request.user.teacher_profile
        return kwargs
    
    def get_success_url(self):
        messages.success(self.request, "Exercício atualizado com sucesso!")
        return reverse('exercise_detail', kwargs={'pk': self.object.pk})

@method_decorator(csrf_protect, name='dispatch')
class ExerciseDeleteView(LoginRequiredMixin, TeacherRequiredMixin, DeleteView):
    model = Exercise
    template_name = 'exercises/exercise_confirm_delete.html'
    success_url = reverse_lazy('exercise_list')
    
    def get_queryset(self):
        # Só permite deletar exercícios que o professor criou
        return Exercise.objects.filter(created_by=self.request.user.teacher_profile)
    
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
    
    def get_queryset(self):
        # Filtra por grupo de classe específico se o parâmetro estiver presente
        class_group_id = self.kwargs.get('class_group_id')
        if class_group_id:
            return Student.objects.filter(
                class_group_id=class_group_id,
                class_group__teacher=self.request.user.teacher_profile
            ).select_related('class_group')
        else:
            # Lista todos os alunos deste professor
            return Student.objects.filter(
                class_group__teacher=self.request.user.teacher_profile
            ).select_related('class_group')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        class_group_id = self.kwargs.get('class_group_id')
        if class_group_id:
            context['class_group'] = get_object_or_404(
                ClassGroup, 
                id=class_group_id,
                teacher=self.request.user.teacher_profile
            )
        return context

@method_decorator(csrf_protect, name='dispatch')
class StudentDetailView(LoginRequiredMixin, TeacherRequiredMixin, DetailView):
    model = Student
    template_name = 'students/student_detail.html'
    context_object_name = 'student'
    
    def get_queryset(self):
        # Garante que o professor só veja seus próprios alunos
        return Student.objects.filter(
            class_group__teacher=self.request.user.teacher_profile
        ).select_related('class_group')

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
        if not self.class_group:
            return self.form_invalid(form)

        # Set manualmente no momento certo
        instance = form.save(commit=False)
        instance.class_group = self.class_group
        instance.save()
        messages.success(self.request, "Aluno cadastrado com sucesso!")
        return redirect(reverse('student_form', kwargs={'class_group_id': self.class_group.pk}))
    
    def get_success_url(self):
        # Redireciona para a lista de alunos da turma
        return reverse_lazy('class_group_students', kwargs={'class_group_id': self.class_group.id})
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['class_group'] = self.class_group
        context['students'] = Student.objects.filter(
            class_group=self.class_group
        ).order_by('first_name', 'last_name')
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
        context['students'] = Student.objects.filter(class_group=self.class_group).order_by('last_name')
        return context

    def form_valid(self, form):
        form.instance.class_group = self.class_group  # Garante que o relacionamento está mantido
        form.save()
        messages.success(self.request, "Aluno atualizado com sucesso!")
        return redirect(reverse('student_form', kwargs={'class_group_id': self.class_group.pk}))


@method_decorator(csrf_protect, name='dispatch')
class StudentDeleteView(LoginRequiredMixin, TeacherRequiredMixin, DeleteView):
    model = Student
    
    def get_queryset(self):
        # Garante que o professor só exclua seus próprios alunos
        return Student.objects.filter(
            class_group__teacher=self.request.user.teacher_profile
        )
    
    def delete(self, request, *args, **kwargs):
        student = self.get_object()
        class_group_id = student.class_group.id
        student.delete()

        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({'success': True})

        messages.success(request, "Aluno excluído com sucesso.")
        return redirect(reverse_lazy('student_form', kwargs={'class_group_id': class_group_id}))
    
    def get_success_url(self):
        return reverse_lazy('student_form', kwargs={'class_group_id': self.object.class_group.id})
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['class_group'] = self.get_object().class_group
        return context
 
 
@method_decorator(csrf_protect, name='dispatch')
class TagCreateView(LoginRequiredMixin, TeacherRequiredMixin, CreateView):
    model = Tag
    fields = ['name', 'type', 'color']
    template_name = 'tag/tag_form.html'
    
    def form_valid(self, form):
        form.instance.teacher = self.request.user.teacher_profile
        messages.success(self.request, "Tag criada com sucesso!")
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse('tag_list')
    
@method_decorator(csrf_protect, name='dispatch')    
class TagListView(LoginRequiredMixin, TeacherRequiredMixin, ListView):
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
        context['type_choices'] = Tag.TYPE_CHOICES
        return context

@method_decorator(csrf_protect, name='dispatch')
class TagCreateView(LoginRequiredMixin, TeacherRequiredMixin, CreateView):
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
class TagUpdateView(LoginRequiredMixin, TeacherRequiredMixin, UpdateView):
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
       
@method_decorator(csrf_protect, name='dispatch')
class QuickAddTagView(LoginRequiredMixin, View):
    def post(self, request, model_type=None, model_id=None):
        tag_name = request.POST.get('tag_name', '').strip().lower()  # Normaliza para minúsculas
        colors = [choice[0] for choice in Tag.COLOR_CHOICES]
        color = random.choice(colors)
        
        if not tag_name:
            messages.error(request, "O nome da tag não pode estar vazio")
            return self.get_redirect_response(model_type, model_id)
        
        # Tipos válidos (protegendo contra valores inválidos)
        valid_types = ['lesson', 'exercise']
        if model_type and model_type not in valid_types:
            raise Http404("Tipo de modelo inválido")
        
        # Verifica se tag já existe para este professor
        existing_tag = Tag.objects.filter(
            name__iexact=tag_name,
            teacher=request.user.teacher_profile
        ).first()
        
        if existing_tag:
            # Verifica se a tag existente é do mesmo tipo
            if model_type and existing_tag.type != model_type:
                messages.warning(request, 
                    f'Tag "{tag_name}" já existe como tipo {existing_tag.get_type_display()}. '
                    f'Crie uma tag específica para {model_type}.')
                return self.get_redirect_response(model_type, model_id)
                
            messages.info(request, f'Tag "{tag_name}" já existe e está disponível para uso')
            tag = existing_tag
        else:
            # Cria nova tag com o tipo específico
            tag = Tag.objects.create(
                name=tag_name,
                teacher=request.user.teacher_profile,
                type=model_type if model_type else 'general',
                color=color
            )
            messages.success(request, f'Nova tag "{tag_name}" criada com sucesso!')
        
        # Remove a associação automática que estava aqui
        return self.get_redirect_response(model_type, model_id)

    def get_redirect_response(self, model_type, model_id):
        """Redireciona para lugar apropriado sem associar a tag"""
        if not model_type or not model_id:
            return HttpResponseRedirect(reverse('tag_list'))
            
        if model_type == 'lesson':
            return HttpResponseRedirect(reverse('lesson_detail', kwargs={'pk': model_id}))
        elif model_type == 'exercise':
            return HttpResponseRedirect(reverse('exercise_detail', kwargs={'pk': model_id}))
