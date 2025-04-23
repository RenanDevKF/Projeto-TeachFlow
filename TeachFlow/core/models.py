from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class Teacher(models.Model):
    """Teacher profile model extending Django's built-in User"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='teacher_profile')
    bio = models.TextField(blank=True)
    subject_area = models.CharField(max_length=100, blank=True)
    phone = models.CharField(max_length=20, blank=True)
    
    def __str__(self):
        return f"{self.user.first_name} {self.user.last_name}"
    
