from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django import forms

from app_perf.models import Admins, Subscribers


class CustomAdminCreationForm(UserCreationForm):

    class Meta(UserCreationForm):
        model = Admins
        fields = ('email',)


class CustomAdminChangeForm(UserChangeForm):

    class Meta:
        model = Admins
        fields = ('email',)


class CustomUserLoginForm(forms.ModelForm):

    class Meta:
        model = Subscribers
        fields = ('email', 'password')


class CustomUserRegisterForm(forms.ModelForm):

    class Meta:
        model = Subscribers
        fields = ('email', 'password', 'timezone_offset')
