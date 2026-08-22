from django.contrib.auth.backends import ModelBackend

from .models import CustomUser
from .utils import normalize_email, normalize_username


class EmailOrUsernameBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        if username is None or password is None:
            return None

        identifier = username.strip()

        try:
            if '@' in identifier:
                user = CustomUser.objects.get(
                    email__iexact=normalize_email(identifier)
                )
            else:
                user = CustomUser.objects.get(
                    username__iexact=normalize_username(identifier)
                )
        except (CustomUser.DoesNotExist, CustomUser.MultipleObjectsReturned):
            return None

        if user.check_password(password) and self.user_can_authenticate(user):
            return user

        return None