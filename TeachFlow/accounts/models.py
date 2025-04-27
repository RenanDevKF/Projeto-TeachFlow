# accounts/models.py
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.db.models.signals import post_save
from django.dispatch import receiver


class SubscriptionPlan(models.TextChoices):
    FREE = 'free', 'Free'
    PRO = 'pro', 'Pro'
    # Adicione outros planos aqui
    
class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, is_teacher=False, **extra_fields):
        if not email:
            raise ValueError('O email é obrigatório')
        email = self.normalize_email(email)
        user = self.model(email=email, is_teacher=is_teacher, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        
        if not extra_fields.get('is_staff'):
            raise ValueError('Superuser precisa ter is_staff=True')
        if not extra_fields.get('is_superuser'):
            raise ValueError('Superuser precisa ter is_superuser=True')
        
        return self.create_user(email, password, **extra_fields)

class CustomUser(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True)
    username = models.CharField(max_length=150, unique=True)
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(default=timezone.now)
    is_teacher = models.BooleanField(default=False)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username','first_name', 'last_name']

    objects = CustomUserManager()

    subscription_plan = models.CharField(
        max_length=20,
        choices=SubscriptionPlan.choices,
        default=SubscriptionPlan.FREE
    )
    
    def __str__(self):
        return self.email

    def validate_email_domain(email):
        if email.endswith('@tempmail.com'):
            raise ValidationError("Email inválido.")

@receiver(post_save, sender=CustomUser)
def create_teacher_profile(sender, instance, created, **kwargs):
    if created and instance.is_teacher:  # Adicione um campo `is_teacher` no CustomUser se necessário
        Teacher.objects.create(user=instance)  


class Teacher(models.Model):
    """Perfil do professor vinculado ao CustomUser"""
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='teacher_profile')
    bio = models.TextField(blank=True)
    subject_area = models.CharField(max_length=100, blank=True)
    phone = models.CharField(max_length=20, blank=True)

    def __str__(self):
        return f"{self.user.first_name} {self.user.last_name}"
            


class Subscription(models.Model):
    user = models.OneToOneField(
        CustomUser, 
        on_delete=models.CASCADE,
        related_name='subscription'
    )
    plan = models.CharField(
        max_length=20,
        choices=SubscriptionPlan.choices,
        default=SubscriptionPlan.FREE
    )
    external_id = models.CharField(max_length=100, blank=True)  # ID do gateway
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.email} - {self.plan}"     