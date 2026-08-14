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
from django.contrib import messages
from django.contrib.auth import login, logout, authenticate, update_session_auth_hash
from django.db import transaction
from django.shortcuts import redirect, render
from django.http import JsonResponse
from .models import CustomUser, Subscription, SubscriptionPlan
from .forms import CustomUserCreationForm, UserProfileForm, TeacherProfileForm, ChangeEmailForm
from .emails import send_account_activation_email, send_email_change_confirmation, send_email_change_notification
from accounts.models import Teacher
from .tokens import get_user_from_activation_token, get_email_change_data
from .utils import normalize_email, normalize_username

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
            user.save()

            if not hasattr(user, 'teacher_profile'):
                Teacher.objects.create(user=user)

            Subscription.objects.create(
                user=user,
                plan=SubscriptionPlan.FREE,
                is_active=True,
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
        profile_form = UserProfileForm(
            instance=request.user,
        )

        teacher_form = TeacherProfileForm(
            instance=request.user.teacher_profile,
        )

        return render(
            request,
            self.template_name,
            {
                'profile_form': profile_form,
                'teacher_form': teacher_form,
            },
        )

    def post(self, request):
        form_type = request.POST.get('form_type')

        if form_type == 'profile_info':
            profile_form = UserProfileForm(
                request.POST,
                instance=request.user,
            )

            teacher_form = TeacherProfileForm(
                request.POST,
                instance=request.user.teacher_profile,
            )

            if profile_form.is_valid() and teacher_form.is_valid():
                with transaction.atomic():
                    profile_form.save()
                    teacher_form.save()

                messages.success(
                    request,
                    'Informações atualizadas com sucesso!',
                )

                return redirect('profile')

            return render(
                request,
                self.template_name,
                {
                    'profile_form': profile_form,
                    'teacher_form': teacher_form,
                    'active_tab': 'personal-info',
                },
                status=400,
            )

        if form_type == 'password_change':
            form = PasswordChangeForm(
                request.user,
                request.POST,
            )

            if form.is_valid():
                user = form.save()

                update_session_auth_hash(
                    request,
                    user,
                )

                messages.success(
                    request,
                    'Senha alterada com sucesso!',
                )
            else:
                for errors in form.errors.values():
                    messages.error(
                        request,
                        errors[0],
                    )

            return redirect('profile')

        return redirect('profile')
    
@method_decorator(csrf_protect, name='dispatch')
@method_decorator(never_cache, name='dispatch')
class ChangeEmailView(LoginRequiredMixin, View):
    template_name = 'accounts/change_email.html'

    def get(self, request):
        form = ChangeEmailForm(request.user)

        return render(
            request,
            self.template_name,
            {'form': form},
        )

    def post(self, request):
        form = ChangeEmailForm(
            request.user,
            request.POST,
        )

        if form.is_valid():
            send_email_change_confirmation(
                request,
                request.user,
                form.cleaned_data['new_email'],
            )

            messages.success(
                request,
                'Enviamos um link de confirmação para o novo e-mail.',
            )

            return redirect('profile')

        return render(
            request,
            self.template_name,
            {'form': form},
            status=400,
        )
        
@method_decorator(never_cache, name='dispatch')
class ConfirmEmailChangeView(LoginRequiredMixin, View):
    def get(self, request, token):
        try:
            data = get_email_change_data(token)
        except signing.SignatureExpired:
            messages.error(
                request,
                'O link de alteração de e-mail expirou. Solicite uma nova alteração.',
            )
            return redirect('profile')
        except signing.BadSignature:
            messages.error(
                request,
                'O link de alteração de e-mail é inválido.',
            )
            return redirect('profile')

        if data.get('user_id') != request.user.pk:
            messages.error(
                request,
                'Este link de alteração de e-mail não pertence à sua conta.',
            )
            return redirect('profile')

        current_email = data.get('current_email')
        new_email = data.get('new_email')
        new_email = normalize_email(new_email)

        if not current_email or not new_email:
            messages.error(
                request,
                'O link de alteração de e-mail é inválido.',
            )
            return redirect('profile')

        if normalize_email(request.user.email) != normalize_email(current_email):
            messages.error(
                request,
                'Este link de alteração de e-mail não é mais válido.',
            )
            return redirect('profile')

        if CustomUser.objects.filter(email__iexact=new_email).exclude(pk=request.user.pk).exists():
            messages.error(
                request,
                'Este e-mail não está mais disponível.',
            )
            return redirect('profile')

        old_email = request.user.email

        request.user.email = new_email
        request.user.save(update_fields=['email'])

        send_email_change_notification(
            request.user,
            old_email,
            new_email,
        )

        messages.success(
            request,
            'E-mail alterado com sucesso!',
        )

        return redirect('profile')
    
 #função isolada para validação de email e username   
def validate_username_email(request):
    username = normalize_username(
        request.GET.get('username')
    )

    email = normalize_email(
        request.GET.get('email')
    )

    data = {
        'is_valid': True,
        'errors': {},
    }

    if username and CustomUser.objects.filter(username__iexact=username).exists():
        data['is_valid'] = False
        data['errors']['username'] = 'Este nome de usuário já está em uso.'

    if email and CustomUser.objects.filter(email__iexact=email).exists():
        data['is_valid'] = False
        data['errors']['email'] = 'Este e-mail já está em uso.'

    return JsonResponse(data)