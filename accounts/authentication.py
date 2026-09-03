from django.contrib.auth.backends import ModelBackend
from django.contrib.auth.models import User

from .models import UserProfile


class AccountNumberBackend(ModelBackend):

    def authenticate(
        self,
        request,
        username=None,
        password=None,
        **kwargs
    ):

        try:
            profile = UserProfile.objects.get(
                account_number=username
            )

            user = profile.user

            if user.check_password(password):
                return user

        except UserProfile.DoesNotExist:
            return None

        return None