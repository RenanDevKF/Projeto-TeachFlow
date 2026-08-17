# accounts/views.py
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.forms import PasswordChangeForm
from django.views.generic import CreateView, UpdateView, View, TemplateView
from django.conf import settings
from django.core import signing
from django.urls import reverse_lazy, reverse
from django.views.decorators.cache import never_cache
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_protect
from django.contrib import messages
from django.contrib.auth import logout, update_session_auth_hash
from django.db import transaction
from django.shortcuts import redirect, render
from django.http import JsonResponse
from .models import CustomUser, Subscription, SubscriptionPlan
from .forms import CustomUserCreationForm, UserProfileForm, TeacherProfileForm, ChangeEmailForm, CustomAuthenticationForm
from .emails import send_account_activation_email, send_email_change_confirmation, send_email_change_notification
from accounts.models import Teacher
from .tokens import get_user_from_activation_token, get_email_change_data
from .utils import normalize_email, normalize_username, validate_username
import logging

logger = logging.getLogger(__name__)

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
            user.email_verified_at = None
            user.save()

            Teacher.objects.create(user=user)

            Subscription.objects.create(
                user=user,
                plan=SubscriptionPlan.FREE,
                is_active=True,
            )

        try:
            send_account_activation_email(
                self.request,
                user,
            )
        except Exception:
            logger.exception(
                'Falha ao enviar e-mail de ativação para o usuário %s.',
                user.pk,
            )

            messages.warning(
                self.request,
                (
                    'Sua conta foi criada, mas não foi possível enviar o e-mail '
                    'de confirmação agora. Tente reenviar o link abaixo.'
                ),
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
                email_verified_at__isnull=True,
            ).first()

            if user:
                try:
                    send_account_activation_email(
                        request,
                        user,
                    )
                except Exception:
                    logger.exception(
                        'Falha ao reenviar e-mail de ativação para o usuário %s.',
                        user.pk,
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

        if user.email_verified_at is not None:
            return render(
                request,
                self.template_name,
                {
                    'activation_status': 'already_active',
                },
            )

        user.email_verified_at = timezone.now()
        user.is_active = True
        user.save(update_fields=['email_verified_at', 'is_active'])

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
    authentication_form = CustomAuthenticationForm
    redirect_authenticated_user = True

    def get_success_url(self):
        if self.request.user.is_superuser:
            return reverse('admin:index')

        return super().get_success_url()

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

        password_form = PasswordChangeForm(
            request.user,
        )

        return render(
            request,
            self.template_name,
            {
                'profile_form': profile_form,
                'teacher_form': teacher_form,
                'password_form': password_form,
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
            password_form = PasswordChangeForm(
                request.user,
                request.POST,
            )

            if password_form.is_valid():
                user = password_form.save()

                update_session_auth_hash(
                    request,
                    user,
                )

                messages.success(
                    request,
                    'Senha alterada com sucesso!',
                )

                return redirect('profile')

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
                    'password_form': password_form,
                    'active_tab': 'password',
                },
                status=400,
            )

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
            try:
                send_email_change_confirmation(
                    request,
                    request.user,
                    form.cleaned_data['new_email'],
                )
            except Exception:
                logger.exception(
                    'Falha ao enviar confirmação de troca de e-mail para o usuário %s.',
                    request.user.pk,
                )

                messages.error(
                    request,
                    (
                        'Não foi possível enviar o e-mail de confirmação agora. '
                        'Tente novamente em alguns instantes.'
                    ),
                )

                return redirect('change_email')

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
        request.user.email_verified_at = timezone.now()
        request.user.save(
            update_fields=[
                'email',
                'email_verified_at',
            ]
        )

        send_email_change_notification(
            request.user,
            old_email,
            new_email,
        )