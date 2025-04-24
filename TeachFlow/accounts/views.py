# accounts/views.py
from django.views.generic import CreateView
from django.urls import reverse_lazy
from django.views.decorators.cache import never_cache
from django.utils.decorators import method_decorator
from django.core.exceptions import ValidationError
from django.contrib import messages
from django.contrib.auth import login
from django.db import transaction
from .models import CustomUser, SubscriptionPlan, Subscription
from core.models import Teacher
import uuid  # Adicionado para gerar IDs únicos

# Defina os planos no nível do módulo ou em core/models.py
class SubscriptionPlan:
    FREE = 'free'
    PRO = 'pro'
    CHOICES = [
        (FREE, 'Free'),
        (PRO, 'Pro'),
    ]

@method_decorator(never_cache, name='dispatch')
class SignupView(CreateView):
    model = CustomUser
    template_name = 'accounts/signup.html'
    fields = ['email', 'first_name', 'last_name', 'password']
    success_url = reverse_lazy('class-group-list')

    def form_valid(self, form):
        try:
            with transaction.atomic():
                # Criação do usuário
                user = form.save(commit=False)
                user.set_password(form.cleaned_data['password'])
                user.is_teacher = True
                user.is_active = True
                user.save()

                # Criação automática do perfil Teacher
                Teacher.objects.create(user=user)

                # Processamento do plano
                plan = self.request.POST.get('plan', SubscriptionPlan.FREE)
                self._process_subscription(user, plan)

                login(self.request, user)
                messages.success(self.request, "Account created successfully!")
                return super().form_valid(form)

        except Exception as e:
            messages.error(self.request, f"Error during signup: {str(e)}")
            return self.form_invalid(form)

    def _process_subscription(self, user, plan):
        """Integração simulada com gateway de pagamento"""
        if plan not in [choice[0] for choice in SubscriptionPlan.CHOICES]:
            raise ValidationError("Invalid subscription plan")

        Subscription.objects.create(
            user=user,
            plan=plan,
            external_id=f'pg_{uuid.uuid4().hex[:12]}',  # ID simulado
            is_active=(plan == SubscriptionPlan.FREE)  # Planos pagos requerem confirmação
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['plans'] = SubscriptionPlan.CHOICES
        return context