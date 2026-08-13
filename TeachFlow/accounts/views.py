# accounts/views.py
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.forms import PasswordChangeForm
from django.views.generic import CreateView, UpdateView, View, TemplateView
from django.conf import settings
from django.core import signing
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
from .emails import send_account_activation_email
from accounts.models import Teacher
from .tokens import get_user_from_activation_token
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
    success_url = reverse_lazy('signup_check_email')

    def form_valid(self, form):
        with transaction.atomic():
            user = form.save(commit=False)
            user.is_teacher = True
            user.is_active = False

            selected_plan = self.request.POST.get(
                'plan',
                SubscriptionPlan.FREE,
            )

            user.subscription_plan = selected_plan
            user.save()

            if not hasattr(user, 'teacher_profile'):
                Teacher.objects.create(user=user)

            try:
                self._process_subscription(
                    user,
                    selected_plan,
                )
            except ValidationError:
                self._process_subscription(
                    user,
                    SubscriptionPlan.FREE,
                )

        send_account_activation_email(
            self.request,
            user,
        )

        if self.request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse(
                {
                    'success': True,
                    'message': (
                        'Cadastro realizado com sucesso. '
                        'Confira seu e-mail para ativar sua conta.'
                    ),
                    'redirect_url': reverse('signup_check_email'),
                }
            )

        return redirect('signup_check_email')
    
    

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
class SignupCheckEmailView(TemplateView):
    template_name = 'accounts/signup_check_email.html'

@method_decorator(csrf_protect, name='dispatch')
@method_decorator(never_cache, name='dispatch')
class ResendActivationEmailView(View):
    def post(self, request):
        email = ' '.join(request.POST.get('email', '').split())

        if email:
            user = CustomUser.objects.filter(
                email__iexact=email,
                is_active=False,
            ).first()

            if user:
                send_account_activation_email(
                    request,
                    user,
                )

        messages.success(
            request,
            (
                'Se existir uma conta aguardando confirmação para este e-mail, '
                'um novo link foi enviado.'
            ),
        )

        return redirect('signup_check_email')

@method_decorator(never_cache, name='dispatch')
class ActivateAccountView(View):
    template_name = 'accounts/account_activation_result.html'

    def get(self, request, token):
        try:
            user = get_user_from_activation_token(token)

        except signing.SignatureExpired:
            return render(
                request,
                self.template_name,
                {
                    'activation_status': 'expired',
                },
                status=400,
            )

        except signing.BadSignature:
            return render(
                request,
                self.template_name,
                {
                    'activation_status': 'invalid',
                },
                status=400,
            )

        if user is None:
            return render(
                request,
                self.template_name,
                {
                    'activation_status': 'invalid',
                },
                status=400,
            )

        if user.is_active:
            return render(
                request,
                self.template_name,
                {
                    'activation_status': 'already_active',
                },
            )

        user.is_active = True
        user.save(update_fields=['is_active'])

        return render(
            request,
            self.template_name,
            {
                'activation_status': 'success',
            },
        )
    
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