from django.urls import path
from . import views
from .views import DuplicateLessonView
from .views import QuickAddTagView, TagListView

urlpatterns = [
    # Class Group URLs
    path('class-groups/', views.ClassGroupListView.as_view(), name='class_group_list'),
    path('class-groups/new/', views.ClassGroupCreateView.as_view(), name='class_group_form'),
    path('class-groups/<int:pk>/', views.ClassGroupDetailView.as_view(), name='class_group_detail'),
    path('class-groups/<int:pk>/edit/', views.ClassGroupUpdateView.as_view(), name='class_group_form'),
    path('class-groups/<int:pk>/delete/', views.ClassGroupDeleteView.as_view(), name='class_group_delete'),
    
    # Student URLs - NOVAS ROTAS
    path('students/', views.StudentListView.as_view(), name='student_list'),
    path('class-groups/<int:class_group_id>/students/', views.StudentListView.as_view(), name='class_group_students'),
    path('class-groups/<int:class_group_id>/students/new/', views.StudentCreateView.as_view(), name='student_form'),
    path('class-groups/<int:class_group_id>/students/<int:pk>/', views.StudentDetailView.as_view(), name='student_detail'),
    path('class-groups/<int:class_group_id>/students/<int:pk>/edit/', views.StudentUpdateView.as_view(), name='student_form'),
    path('class-groups/<int:class_group_id>/students/<int:pk>/delete/', views.StudentDeleteView.as_view(), name='student_delete'),
    
    # Lesson URLs
    path('lessons/', views.LessonListView.as_view(), name='lesson_list'),
    path('class-groups/<int:class_group_id>/lessons/', views.LessonListView.as_view(), name='group_lessons'),
    path('lessons/new/', views.LessonCreateView.as_view(), name='lesson_form'),
    path('lessons/<int:pk>/duplicate/', views.DuplicateLessonView.as_view(), name='duplicate_lesson'),
    path('lessons/<int:pk>/', views.LessonDetailView.as_view(), name='lesson_detail'),
    path('lessons/<int:pk>/edit/', views.LessonUpdateView.as_view(), name='lesson_form'),
    path('lessons/<int:pk>/delete/', views.LessonDeleteView.as_view(), name='lesson_delete'),
    
    # Exercise URLs
    path('exercises/', views.ExerciseListView.as_view(), name='exercise_list'),
    path('exercises/new/', views.ExerciseCreateView.as_view(), name='exercise_form'),
    path('exercises/<int:pk>/', views.ExerciseDetailView.as_view(), name='exercise_detail'),
    path('exercises/<int:pk>/edit/', views.ExerciseUpdateView.as_view(), name='exercise_form'),
    path('exercises/<int:pk>/delete/', views.ExerciseDeleteView.as_view(), name='exercise_delete'),
    
    # Learning Objective URLs
    path('objectives/', views.LearningObjectiveListView.as_view(), name='objective-list'),
    path('objectives/new/', views.LearningObjectiveCreateView.as_view(), name='objective-create'),
    
    # Future Ideas URLs
    path('ideas/', views.FutureIdeaListView.as_view(), name='idea-list'),
    path('ideas/new/', views.FutureIdeaCreateView.as_view(), name='idea-create'),
    
    path('dashboard/', views.dashboard_view, name='dashboard'),
    
    path('tags/', views.TagListView.as_view(), name='tag_list'),
    path('tags/new/', views.TagCreateView.as_view(), name='tag_form'),
    path('tags/<int:pk>/edit/', views.TagUpdateView.as_view(), name='tag_update'),
    path('tags/add/<str:model_type>/<int:model_id>/', QuickAddTagView.as_view(), name='quick_add_tag'),
    
]