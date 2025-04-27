# accounts/views.py
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import CreateView, UpdateView
from django.urls import reverse_lazy, reverse
from django.views.decorators.cache import never_cache
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_protect
from django.core.exceptions import ValidationError
from django.contrib import messages
from django.contrib.auth import login, logout, authenticate
from django.db import transaction
from django.shortcuts import redirect
from django.http import JsonResponse
from .models import CustomUser, Subscription
from .forms import CustomUserCreationForm
from accounts.models import Teacher
import uuid  # Adicionado para gerar IDs únicos

# Defina os planos no nível do módulo ou em core/models.py
class SubscriptionPlan:
    FREE = 'free'
    PRO = 'pro'
    CHOICES = [
        (FREE, 'Free'),
        (PRO, 'Pro'),
    ]
@method_decorator(csrf_protect, name='dispatch')
@method_decorator(never_cache, name='dispatch')
class SignupView(CreateView):
    model = CustomUser
    template_name = 'accounts/signup.html'
    form_class = CustomUserCreationForm
    success_url = reverse_lazy('login')

    def form_valid(self, form):
        user = form.save(commit=False)
        user.is_teacher = True
        user.is_active = True
        user.save()
        
        if not hasattr(user, 'teacher_profile'):
            Teacher.objects.create(user=user)

        selected_plan = self.request.POST.get('selected_plan', 'free')
        if selected_plan == 'basic':
            pass
        elif selected_plan == 'premium':
            pass
        else:
            pass

        if self.request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': True,
                'message': 'Cadastro realizado com sucesso!',
                'redirect_url': reverse('login')
            })
        
        return redirect('login')
    
    

    def form_invalid(self, form):
        if self.request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': False,
                'error': 'Erro de validação',
                'errors': {
                    field: [str(e) for e in errors]
                    for field, errors in form.errors.items()
                }
            }, status=400)
        return super().form_invalid(form)

    def handle_exception(self, request, exception):
        """Captura exceções não tratadas"""
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': False,
                'error': 'Erro interno',
                'detail': str(exception)
            }, status=500)
        raise exception

    def _process_subscription(self, user, plan):
        """Integração simulada com gateway de pagamento"""
        if plan not in [choice[0] for choice in SubscriptionPlan.CHOICES]:
            raise ValidationError("Invalid subscription plan")

        Subscription.objects.create(
            user=user,
            plan=plan,
            external_id=f'pg_{uuid.uuid4().hex[:12]}',
            is_active=(plan == SubscriptionPlan.FREE)
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['plans'] = SubscriptionPlan.CHOICES
        return context
    
@method_decorator(never_cache, name='dispatch')
class CustomLoginView(LoginView):
    template_name = 'accounts/login.html'
    redirect_authenticated_user = True
    
    def get_success_url(self):
        # Redireciona superusuários diretamente para o admin
        if self.request.user.is_superuser:
            return reverse('admin:index')
        return super().get_success_url()

    def post(self, request, *args, **kwargs):
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            # Lógica para AJAX
            email = request.POST.get('email')
            password = request.POST.get('password')
            user = authenticate(request, username=email, password=password)
            
            if user is not None:
                login(request, user)
                return JsonResponse({
                    'success': True,
                    'redirect_url': self.get_success_url()
                })
            else:
                return JsonResponse({
                    'success': False,
                    'error': 'Email ou senha inválidos'
                }, status=400)
        
        # Fallback para comportamento padrão
        return super().post(request, *args, **kwargs)

@method_decorator(never_cache, name='dispatch')
class CustomLogoutView(LogoutView):
    next_page = reverse_lazy('login')

# View de perfil
@method_decorator(never_cache, name='dispatch')
class ProfileUpdateView(LoginRequiredMixin, UpdateView):
    model = CustomUser
    fields = ['first_name', 'last_name', 'email']
    template_name = 'accounts/profile.html'
    success_url = reverse_lazy('profile')
    
    def get_object(self):
        return self.request.user
    
    
 #função isolada para validação de email e username   
def validate_username_email(request):
    username = request.GET.get('username', None)
    email = request.GET.get('email', None)
    data = {'is_valid': True, 'errors': {}}

    if username and CustomUser.objects.filter(username=username).exists():
        data['is_valid'] = False
        data['errors']['username'] = "Este nome de usuário já está em uso."

    if email and CustomUser.objects.filter(email=email).exists():
        data['is_valid'] = False
        data['errors']['email'] = "Este email já está em uso."

    return JsonResponse(data)