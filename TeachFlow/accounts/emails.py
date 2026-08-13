from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.urls import reverse

from .tokens import make_activation_token


def send_account_activation_email(request, user):
    token = make_activation_token(user)

    activation_url = request.build_absolute_uri(
        reverse(
            'activate_account',
            kwargs={'token': token},
        )
    )

    message = render_to_string(
        'accounts/emails/account_activation.txt',
        {
            'user': user,
            'activation_url': activation_url,
        },
    )

    send_mail(
        subject='Confirme seu e-mail no TeachFlow',
        message=message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[user.email],
        fail_silently=False,
    )