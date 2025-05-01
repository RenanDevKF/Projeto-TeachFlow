from django.urls import path
from . import views

urlpatterns = [
    # Class Group URLs
    path('class-groups/', views.ClassGroupListView.as_view(), name='class_group_list'),
    path('class-groups/new/', views.ClassGroupCreateView.as_view(), name='class_group_create'),
    path('class-groups/<int:pk>/', views.ClassGroupDetailView.as_view(), name='class_group_detail'),
    path('class-groups/<int:pk>/edit/', views.ClassGroupUpdateView.as_view(), name='class_group_update'),
    path('class-groups/<int:pk>/delete/', views.ClassGroupDeleteView.as_view(), name='class_group_delete'),
    
    # Student URLs - NOVAS ROTAS
    path('students/', views.StudentListView.as_view(), name='student_list'),
    path('class-groups/<int:class_group_id>/students/', views.StudentListView.as_view(), name='class_group_students'),
    path('class-groups/<int:class_group_id>/students/new/', views.StudentCreateView.as_view(), name='student_create'),
    path('students/<int:pk>/', views.StudentDetailView.as_view(), name='student_detail'),
    path('class-groups/<int:class_group_id>/students/<int:pk>/edit/', views.StudentUpdateView.as_view(), name='student_update'),
    path('class-groups/<int:class_group_id>/students/<int:pk>/delete/', views.StudentDeleteView.as_view(), name='student_delete'),
    
    # Lesson URLs
    path('lessons/', views.LessonListView.as_view(), name='lesson_list'),
    path('class-groups/<int:class_group_id>/lessons/', views.LessonListView.as_view(), name='group_lessons'),
    path('lessons/new/', views.LessonCreateView.as_view(), name='lesson_create'),
    path('lessons/<int:pk>/', views.LessonDetailView.as_view(), name='lesson-detail'),
    path('lessons/<int:pk>/edit/', views.LessonUpdateView.as_view(), name='lesson-update'),
    path('lessons/<int:pk>/delete/', views.LessonDeleteView.as_view(), name='lesson-delete'),
    
    # Exercise URLs
    path('exercises/', views.ExerciseListView.as_view(), name='exercise_list'),  # Adicione esta linha
    path('lessons/<int:lesson_id>/exercises/new/', views.ExerciseCreateView.as_view(), name='exercise-create'),
    
    # Learning Objective URLs
    path('objectives/', views.LearningObjectiveListView.as_view(), name='objective-list'),
    path('objectives/new/', views.LearningObjectiveCreateView.as_view(), name='objective-create'),
    
    # Future Ideas URLs
    path('ideas/', views.FutureIdeaListView.as_view(), name='idea-list'),
    path('ideas/new/', views.FutureIdeaCreateView.as_view(), name='idea-create'),
    
    path('dashboard/', views.dashboard_view, name='dashboard'),
    
]