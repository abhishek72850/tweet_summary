from django.contrib import admin
from django.urls import path, include
from . import views

urlpatterns = [
    path('register', views.RegisterUser.as_view()),
    path('add', views.UpsertSubscription.as_view()),
    path('view_or_update', views.ViewOrUpdateUserAllDetails.as_view()),
    path('unsubscribe', views.UnSubscribe.as_view()),
    path('confirm_email', views.ConfirmEmail.as_view()),
    path('confirm_subscription', views.ConfirmSubscription.as_view())
]
