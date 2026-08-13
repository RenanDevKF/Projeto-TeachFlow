from django.conf import settings
from django.core import signing

from .models import CustomUser


ACTIVATION_SALT = 'accounts.email_activation'


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