from django.contrib import admin
from django.urls import path, include
from . import views

urlpatterns = [
    path('fetch/summary/', views.SummaryAnalysis.as_view())

]