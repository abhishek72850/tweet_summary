from django.contrib import admin
from django.urls import path, include
from django.contrib.auth.decorators import login_required

from app_ui import views

urlpatterns = [
    path('', views.home_login_view, name='home_login'),
    path('logout', views.logout_view, name='home_logout'),
    path('home/', views.home_view, name='home'),
    path('register/', views.register_view, name='register'),
    path('subscribe/', views.create_subscription_view, name='subscribe'),
    path('quick_analysis/', views.quick_analysis_view, name='quick_analysis'),
    path('user_plans/', views.user_plans_view, name='user_plans'),
    path('account/', views.account_details_view, name='account_details'),
    path('change_password/', views.change_password_view, name='change_password'),
    path('forgot_password/', views.forgot_password_view, name='forgot_password'),
    path('reset_password/', views.reset_password_view, name='reset_password'),
]
