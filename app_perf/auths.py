from django.contrib.auth.backends import ModelBackend
from rest_framework import authentication
from app_perf.models import Subscribers


class CustomUserAuthentication(authentication.BaseAuthentication):
    def authenticate(self, request, email=None, password=None):
        try:
            user = Subscribers.objects.get(email=email, password=password)
        except Subscribers.DoesNotExist:
            return None
        return user

    def get_user(self, subscriber_id):
        try:
            return Subscribers.objects.get(id=subscriber_id)
        except Subscribers.DoesNotExist:
            return None
