from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.urls import reverse

from .tokens import make_activation_token, make_email_change_token


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
    
def send_email_change_confirmation(request, user, new_email):
    token = make_email_change_token(user, new_email)

    confirmation_url = request.build_absolute_uri(
        reverse(
            'confirm_email_change',
            kwargs={'token': token},
        )
    )

    message = render_to_string(
        'accounts/emails/email_change_confirmation.txt',
        {
            'user': user,
            'new_email': new_email,
            'confirmation_url': confirmation_url,
        },
    )

    send_mail(
        subject='Confirme seu novo e-mail no TeachFlow',
        message=message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[new_email],
        fail_silently=False,
    )
    
def send_email_change_notification(user, old_email, new_email):
    message = render_to_string(
        'accounts/emails/email_change_notification.txt',
        {
            'user': user,
            'old_email': old_email,
            'new_email': new_email,
        },
    )

    send_mail(
        subject='O e-mail da sua conta TeachFlow foi alterado',
        message=message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[old_email],
        fail_silently=True,
    )