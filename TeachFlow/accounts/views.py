# accounts/views.py
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.forms import PasswordChangeForm
from django.views.generic import CreateView, UpdateView, View
from django.urls import reverse_lazy, reverse
from django.views.decorators.cache import never_cache
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_protect
from django.core.exceptions import ValidationError
from django.contrib import messages
from django.contrib.auth import login, logout, authenticate, update_session_auth_hash
from django.db import transaction
from django.shortcuts import redirect, render
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
        selected_plan = self.request.POST.get('plan', SubscriptionPlan.FREE)
        user.subscription_plan = selected_plan
        user.save()
        
        if not hasattr(user, 'teacher_profile'):
            Teacher.objects.create(user=user)

        try:
            # 🔥 Processa a assinatura conforme o plano selecionado
            self._process_subscription(user, selected_plan)
        except ValidationError:
            # Fallback: Se o plano for inválido, inscreve no gratuito
            self._process_subscription(user, SubscriptionPlan.FREE)

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
class ProfileView(LoginRequiredMixin, View):
    template_name = 'accounts/profile.html'
    
    def get(self, request):
        return render(request, self.template_name)
    
    def post(self, request):
        form_type = request.POST.get('form_type')
        
        if form_type == 'profile_info':
            # Atualizar informações do perfil
            user = request.user
            user.first_name = request.POST.get('first_name')
            user.last_name = request.POST.get('last_name')
            user.email = request.POST.get('email')
            user.save()
            
            # Atualizar perfil do professor
            teacher_profile = user.teacher_profile
            teacher_profile.display_name = request.POST.get('display_name')
            teacher_profile.phone = request.POST.get('phone')
            teacher_profile.subject_area = request.POST.get('subject_area')
            teacher_profile.bio = request.POST.get('bio')
            teacher_profile.save()
            
            messages.success(request, 'Informações atualizadas com sucesso!')
            
        elif form_type == 'password_change':
            # Atualizar senha
            form = PasswordChangeForm(request.user, request.POST)
            if form.is_valid():
                user = form.save()
                update_session_auth_hash(request, user)  # Importante para manter a sessão ativa
                messages.success(request, 'Senha alterada com sucesso!')
            else:
                for error in form.errors.values():
                    messages.error(request, error[0])
                
        elif form_type == 'subscription_change':
            # Atualizar plano de assinatura
            plan = request.POST.get('plan')
            if plan in [choice[0] for choice in SubscriptionPlan.CHOICES]:
                user = request.user
                
                # Atualizar plano no perfil do usuário
                user.subscription_plan = plan
                user.save()
                
                # Atualizar ou criar registro de assinatura
                subscription, created = Subscription.objects.get_or_create(
                    user=user,
                    defaults={
                        'plan': plan,
                        'external_id': f'pg_{uuid.uuid4().hex[:12]}',
                        'is_active': True
                    }
                )
                
                if not created:
                    subscription.plan = plan
                    subscription.is_active = True
                    subscription.save()
                
                messages.success(request, f'Plano atualizado para {dict(SubscriptionPlan.CHOICES)[plan]}!')
            else:
                messages.error(request, 'Plano inválido!')
                
        return redirect('profile')
    
    
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