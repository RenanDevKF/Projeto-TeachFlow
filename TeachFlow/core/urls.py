from django.urls import path
from . import views

urlpatterns = [
    # Class Group URLs
    path('class-groups/', views.ClassGroupListView.as_view(), name='class-group-list'),
    path('class-groups/new/', views.ClassGroupCreateView.as_view(), name='class-group-create'),
    path('class-groups/<int:pk>/', views.ClassGroupDetailView.as_view(), name='class-group-detail'),
    path('class-groups/<int:pk>/edit/', views.ClassGroupUpdateView.as_view(), name='class-group-update'),
    path('class-groups/<int:pk>/delete/', views.ClassGroupDeleteView.as_view(), name='class-group-delete'),
    
    # Lesson URLs
    path('class-groups/<int:class_group_id>/lessons/', views.LessonListView.as_view(), name='lesson-list'),
    path('lessons/new/<int:class_group_id>/', views.LessonCreateView.as_view(), name='lesson-create'),
    path('lessons/<int:pk>/', views.LessonDetailView.as_view(), name='lesson-detail'),
    path('lessons/<int:pk>/edit/', views.LessonUpdateView.as_view(), name='lesson-update'),
    path('lessons/<int:pk>/delete/', views.LessonDeleteView.as_view(), name='lesson-delete'),
    
    # Exercise URLs
    path('lessons/<int:lesson_id>/exercises/new/', views.ExerciseCreateView.as_view(), name='exercise-create'),
    
    # Learning Objective URLs
    path('objectives/', views.LearningObjectiveListView.as_view(), name='objective-list'),
    path('objectives/new/', views.LearningObjectiveCreateView.as_view(), name='objective-create'),
    
    # Future Ideas URLs
    path('ideas/', views.FutureIdeaListView.as_view(), name='idea-list'),
    path('ideas/new/', views.FutureIdeaCreateView.as_view(), name='idea-create'),
]