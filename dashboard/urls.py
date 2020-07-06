from django.contrib import admin
from django.urls import path, include
from . import views

urlpatterns = [
    path('dashboard', views.dashboard),
    path('panel', views.choice_panel),
    path('portal', views.choice_portal)
]
