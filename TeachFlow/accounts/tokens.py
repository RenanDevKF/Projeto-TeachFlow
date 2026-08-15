from django.conf import settings
from django.core import signing

from .models import CustomUser


ACTIVATION_SALT = 'accounts.email_activation'
EMAIL_CHANGE_SALT = 'accounts.email_change'


def make_activation_token(user):
    return signing.dumps(
        {
            'user_id': user.pk,
            'email': user.email,
        },
        salt=ACTIVATION_SALT,
        compress=True,
    )


def get_user_from_activation_token(token):
    data = signing.loads(
        token,
        salt=ACTIVATION_SALT,
        max_age=settings.ACCOUNT_ACTIVATION_TIMEOUT,
    )

    return CustomUser.objects.filter(
        pk=data.get('user_id'),
        email__iexact=data.get('email'),
    ).first()

def make_email_change_token(user, new_email):
    return signing.dumps(
        {
            'user_id': user.pk,
            'current_email': user.email,
            'new_email': new_email,
        },
        salt=EMAIL_CHANGE_SALT,
        compress=True,
    )


def get_email_change_data(token):
    return signing.loads(
        token,
        salt=EMAIL_CHANGE_SALT,
        max_age=settings.EMAIL_CHANGE_TIMEOUT,
    )