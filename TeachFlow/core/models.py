from django.db import models
from django.utils import timezone
from django.contrib.admin.models import LogEntry
from accounts.models import Teacher
import random


class ClassGroup(models.Model):
    """Represents a class or group of students"""
    PERIOD_CHOICES = [
        ('Manhã', 'Manhã'),
        ('Tarde', 'Tarde'),
        ('Noite', 'Noite'),
    ]
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    school = models.CharField(max_length=100, blank=True)
    period = models.CharField(max_length=10, choices=PERIOD_CHOICES, blank=True)
    schedule = models.CharField(max_length=50, blank=True, null=True, verbose_name="Horário")  # NOVA LINHA
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE, related_name='class_groups')
    year = models.IntegerField(default=timezone.now().year)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:  # NOVA SEÇÃO
        ordering = ['period', 'schedule', 'name']
    
    def __str__(self):
        return f"{self.name} ({self.teacher})"
    
class Student(models.Model):
    """Student model with basic information"""
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    class_group = models.ForeignKey(ClassGroup, on_delete=models.CASCADE, related_name='students')
    notes = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.first_name} {self.last_name}"
    
    class Meta:
        ordering = ['first_name','last_name']
        
class Tag(models.Model):
    TYPE_CHOICES = [
        ('lesson', 'Aula'),
        ('exercise', 'Exercício'),
        ('general', 'Geral')
    ]
    
    # Cores pré-definidas (cores Tailwind CSS)
    COLOR_CHOICES = [
        ('#3B82F6', 'Azul'),       # bg-blue-500
        ('#10B981', 'Verde'),      # bg-green-500
        ('#F59E0B', 'Amarelo'),    # bg-yellow-500
        ('#8B5CF6', 'Roxo'),       # bg-purple-500
        ('#EC4899', 'Rosa'),       # bg-pink-500
        ('#6366F1', 'Índigo'),     # bg-indigo-500
        ('#EF4444', 'Vermelho'),   # bg-red-500
        ('#14B8A6', 'Turquesa'),   # bg-teal-500
    ]
    
    name = models.CharField(max_length=50)
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE, related_name='tags')
    color = models.CharField(max_length=7, choices=COLOR_CHOICES, default='#3B82F6')
    type = models.CharField(max_length=10, choices=TYPE_CHOICES, default='general')
    
    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        if not self.color:
            # Atribui uma cor aleatória se não tiver definida
            self.color = random.choice(self.COLOR_CHOICES)[0]
        super().save(*args, **kwargs)
    
class LearningObjective(models.Model):
    """Learning objectives defined by curriculum or teacher"""
    title = models.CharField(max_length=200)
    description = models.TextField()
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE, related_name='learning_objectives')
    tags = models.ManyToManyField(Tag, blank=True, related_name='objectives')
    
    def __str__(self):
        return self.title
    
class Lesson(models.Model):
    """Represents a lesson taught to a class group"""
    class_group = models.ForeignKey(ClassGroup, on_delete=models.CASCADE, related_name='lessons')
    date = models.DateField()
    title = models.CharField(max_length=200)
    content = models.TextField()
    performance_notes = models.TextField(blank=True)
    exercises = models.ManyToManyField('Exercise', blank=True, related_name='lessons')
    objectives = models.ManyToManyField(LearningObjective, blank=True, related_name='lessons')
    tags = models.ManyToManyField(Tag, blank=True, related_name='lessons')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.title} - {self.date}"
    
    class Meta:
        ordering = ['-date']
        
class Exercise(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    duration = models.IntegerField(help_text="Duration in minutes", null=True, blank=True)
    materials = models.TextField(blank=True)
    created_by = models.ForeignKey(Teacher, on_delete=models.CASCADE, related_name='exercises')
    objectives = models.ManyToManyField(LearningObjective, blank=True, related_name='exercises')
    tags = models.ManyToManyField(Tag, blank=True, related_name='exercises')
    is_template = models.BooleanField(default=False, help_text="Exercício modelo para reutilização")
    
    class Meta:
        ordering = ['title']
        verbose_name = 'Exercício'
        verbose_name_plural = 'Exercícios'
        
    def belongs_to_teacher(self, teacher):
        return self.created_by == teacher or self.lessons.filter(
            class_group__teacher=teacher
        ).exists()
    
    def __str__(self):
        return self.title
    
class FutureIdea(models.Model):
    """Storage for future lesson ideas and notes"""
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE, related_name='future_ideas')
    title = models.CharField(max_length=200)
    description = models.TextField()
    class_group = models.ForeignKey(ClassGroup, on_delete=models.SET_NULL, null=True, blank=True, related_name='future_ideas')
    tags = models.ManyToManyField(Tag, blank=True, related_name='future_ideas')
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.title
    
class AdminActionLog(models.Model):
    ACTION_CHOICES = [
        ('create', 'Criação'),
        ('update', 'Atualização'),
        ('delete', 'Exclusão'),
        ('other', 'Outro')
    ]

    user = models.ForeignKey(
        'accounts.CustomUser',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,  # Permite registro sem usuário (caso o usuário seja deletado)
        verbose_name='Usuário'
    )
    action = models.CharField(
        max_length=100,
        choices=ACTION_CHOICES,
        verbose_name='Ação'
    )
    model_name = models.CharField(
        max_length=100,
        verbose_name='Modelo afetado'
    )
    object_id = models.IntegerField(
        verbose_name='ID do Objeto'
    )
    details = models.JSONField(
        null=True,
        blank=True,
        verbose_name='Detalhes (JSON)'
    )
    timestamp = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Data/Hora'
    )

    class Meta:
        verbose_name = 'Log de Ação'
        verbose_name_plural = 'Logs de Ações'
        ordering = ['-timestamp']  # Mais recentes primeiro

    def __str__(self):
        return f"{self.get_action_display()} em {self.model_name} (ID: {self.object_id})"