from django.contrib import admin
from django.contrib.auth.models import User, Group
from django.db.models import Q
from django.utils.html import format_html
from django.urls import reverse

from .models import (
    ClassGroup, Student, Lesson, Exercise, 
    Tag, LearningObjective, FutureIdea, AdminActionLog
)

# Security-enhanced admin configuration
class SecureModelAdmin(admin.ModelAdmin):
    """Base admin class with enhanced security features"""
    def has_module_permission(self, request):
        # Only superusers can access these models in admin
        return request.user.is_superuser
    
    def has_view_permission(self, request, obj=None):
        return request.user.is_superuser
    
    def has_change_permission(self, request, obj=None):
        return request.user.is_superuser
    
    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser
    
    # Impede deleção em massa (só deleta um por um)
    def has_delete_permission(self, request, obj=None):
        if obj and request.user.is_superuser:
            return True
        return False

    # Remove a ação "Deletar selecionados" do dropdown
    actions = None


@admin.register(ClassGroup)
class ClassGroupAdmin(SecureModelAdmin):
    list_display = ('name', 'teacher_name', 'year', 'is_active', 'student_count', 'lesson_count')
    list_filter = ('is_active', 'year', 'teacher')
    search_fields = ('name', 'teacher__user__username', 'teacher__user__first_name')
    readonly_fields = ('created_at', 'updated_at')
    
    def teacher_name(self, obj):
        return f"{obj.teacher.user.first_name} {obj.teacher.user.last_name}"
    teacher_name.short_description = "Teacher"
    
    def student_count(self, obj):
        count = obj.students.count()
        url = reverse('admin:core_student_changelist') + f'?class_group__id__exact={obj.id}'
        return format_html('<a href="{}">{} students</a>', url, count)
    student_count.short_description = "Students"
    
    def lesson_count(self, obj):
        count = obj.lessons.count()
        url = reverse('admin:core_lesson_changelist') + f'?class_group__id__exact={obj.id}'
        return format_html('<a href="{}">{} lessons</a>', url, count)
    lesson_count.short_description = "Lessons"
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'description', 'teacher', 'year', 'is_active')
        }),
        ('System Information', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(Student)
class StudentAdmin(SecureModelAdmin):
    list_display = ('full_name', 'class_group', 'teacher', 'is_active')
    list_filter = ('is_active', 'class_group', 'class_group__teacher')
    search_fields = ('first_name', 'last_name', 'notes')
    readonly_fields = ('created_at',)
    
    def full_name(self, obj):
        return f"{obj.first_name} {obj.last_name}"
    full_name.short_description = "Student Name"
    
    def teacher(self, obj):
        return obj.class_group.teacher
    teacher.short_description = "Teacher"
    
    fieldsets = (
        ('Student Information', {
            'fields': ('first_name', 'last_name', 'class_group', 'is_active')
        }),
        ('Additional Information', {
            'fields': ('notes',),
        }),
        ('System Information', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )


@admin.register(Lesson)
class LessonAdmin(SecureModelAdmin):
    list_display = ('title', 'class_group', 'teacher_name', 'date', 'exercise_count')
    list_filter = ('date', 'class_group', 'class_group__teacher')
    search_fields = ('title', 'content', 'class_group__name')
    readonly_fields = ('created_at', 'updated_at')
    filter_horizontal = ('objectives', 'tags')
    date_hierarchy = 'date'
    
    def teacher_name(self, obj):
        return obj.class_group.teacher
    teacher_name.short_description = "Teacher"
    
    def exercise_count(self, obj):
        count = obj.exercises.count()
        url = reverse('admin:core_exercise_changelist') + f'?lesson__id__exact={obj.id}'
        return format_html('<a href="{}">{} exercises</a>', url, count)
    exercise_count.short_description = "Exercises"
    
    def get_list_filter(self, request):
        if request.user.is_superuser:
            return ('date', 'class_group', 'class_group__teacher')  # Filtros completos
        return ('date', 'class_group')  # Filtros limitados
    
    fieldsets = (
        ('Lesson Information', {
            'fields': ('class_group', 'date', 'title', 'content')
        }),
        ('Assessment', {
            'fields': ('performance_notes',),
        }),
        ('Related Content', {
            'fields': ('objectives', 'tags'),
        }),
        ('System Information', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(Exercise)
class ExerciseAdmin(SecureModelAdmin):
    list_display = ('title', 'created_by', 'duration', 'is_template', 'exercises_count', 'tags_list')
    list_filter = ('created_by', 'is_template', 'tags')
    search_fields = ('title', 'description', 'materials')
    filter_horizontal = ('objectives', 'tags')
    readonly_fields = ('created_by', 'related_lessons')
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'description', 'created_by', 'is_template')
        }),
        ('Details', {
            'fields': ('duration', 'materials'),
        }),
        ('Relationships', {
            'fields': ('objectives', 'tags'),
        }),
        ('Usage', {
            'fields': ('related_lessons',),
            'classes': ('collapse',)
        }),
    )

    def exercises_count(self, obj):
        return obj.lessons.count()
    exercises_count.short_description = 'Usado em (aulas)'

    def tags_list(self, obj):
        return ", ".join([t.name for t in obj.tags.all()])
    tags_list.short_description = 'Tags'

    def related_lessons(self, obj):
        lessons = obj.lessons.select_related('class_group').all()
        return mark_safe("<br>".join(
            f'<a href="{reverse("admin:core_lesson_change", args=[l.id])}">{l.title} ({l.date} - {l.class_group.name})</a>'
            for l in lessons
        ))
    related_lessons.short_description = 'Aulas que usam este exercício'

    def get_list_filter(self, request):
        list_filter = super().get_list_filter(request)
        if request.user.is_superuser:
            list_filter += ('created_by',)
        return list_filter

    def save_model(self, request, obj, form, change):
        if not obj.pk:  # Se for criação
            obj.created_by = request.user.teacher_profile
        super().save_model(request, obj, form, change)


@admin.register(Tag)
class TagAdmin(SecureModelAdmin):
    list_display = ('name', 'teacher', 'color', 'usage_count')
    list_filter = ('teacher',)
    search_fields = ('name',)
    
    def usage_count(self, obj):
        lessons = obj.lessons.count()
        exercises = obj.exercises.count()
        objectives = obj.objectives.count()
        return f"{lessons} lessons, {exercises} exercises, {objectives} objectives"
    usage_count.short_description = "Usage"
    
    fieldsets = (
        ('Tag Information', {
            'fields': ('name', 'color', 'teacher')
        }),
    )


@admin.register(LearningObjective)
class LearningObjectiveAdmin(SecureModelAdmin):
    list_display = ('title', 'teacher', 'usage_count')
    list_filter = ('teacher', 'tags')
    search_fields = ('title', 'description')
    filter_horizontal = ('tags',)
    
    def usage_count(self, obj):
        lessons = obj.lessons.count()
        exercises = obj.exercises.count()
        return f"{lessons} lessons, {exercises} exercises"
    usage_count.short_description = "Usage"
    
    fieldsets = (
        ('Objective Information', {
            'fields': ('title', 'description', 'teacher')
        }),
        ('Categorization', {
            'fields': ('tags',),
        }),
    )


@admin.register(FutureIdea)
class FutureIdeaAdmin(SecureModelAdmin):
    list_display = ('title', 'teacher', 'class_group', 'created_at')
    list_filter = ('teacher', 'class_group', 'created_at')
    search_fields = ('title', 'description')
    readonly_fields = ('created_at',)
    filter_horizontal = ('tags',)
    
    fieldsets = (
        ('Idea Information', {
            'fields': ('title', 'description', 'teacher', 'class_group')
        }),
        ('Categorization', {
            'fields': ('tags',),
        }),
        ('System Information', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )

class AdminActionLogAdmin(SecureModelAdmin):
    list_display = ('user', 'action', 'model_name', 'object_id', 'timestamp')
    readonly_fields = ('user', 'action', 'model_name', 'object_id', 'timestamp')

# Optional: Customize the admin site header and title
admin.site.site_header = "Teaching Assistant Admin"
admin.site.site_title = "Teaching Assistant"
admin.site.index_title = "Administration Panel"

# Unregister models that aren't needed for the technical staff
admin.site.unregister(Group)

@admin.register(AdminActionLog)
class AdminActionLogAdmin(admin.ModelAdmin):
    list_display = ('action', 'model_name', 'object_id', 'user', 'timestamp')
    list_filter = ('action', 'model_name', 'timestamp')
    search_fields = ('user__email', 'model_name', 'object_id')
    readonly_fields = ('timestamp',)  # Evita edição da data
    date_hierarchy = 'timestamp'  # Navegação por datas