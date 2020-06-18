from django.contrib import admin
from django.urls import path, include
from . import views

urlpatterns = [
    path('add', views.UpsertSubscriber.as_view()),
    path('unsubscribe', views.UnSubscribe.as_view()),
    path('confirm_email', views.ConfirmSubscription.as_view())
]
