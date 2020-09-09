from django.shortcuts import render, redirect
from django.contrib.auth import logout

from helpers.db import get_account_details
# Create your views here.


def home_login_view(request):
    return render(request, 'app_ui/index.html')


def logout_view(request):
    logout(request)
    return redirect('home_login')


def home_view(request):
    if not request.user.is_authenticated:
        return redirect('home_login')
    return render(request, 'app_ui/loggedIn.html')


def register_view(request):
    return render(request, 'app_ui/register.html')


def create_subscription_view(request):
    if not request.user.is_authenticated:
        return redirect('home_login')
    return render(request, 'app_ui/subscribePage.html')


def quick_analysis_view(request):
    if not request.user.is_authenticated:
        return redirect('home_login')
    return render(request, 'app_ui/quickAnalysis.html')


def user_plans_view(request):
    if not request.user.is_authenticated:
        return redirect('home_login')
    return render(request, 'app_ui/plans.html')


def account_details_view(request):
    if not request.user.is_authenticated:
        return redirect('home_login')
    return render(request, 'app_ui/viewdetails.html')


def change_password_view(request):
    if not request.user.is_authenticated:
        return redirect('home_login')
    return render(request, 'app_ui/changePassword.html')


def forgot_password_view(request):
    return render(request, 'app_ui/forgotPassword.html')


def reset_password_view(request):
    return render(request, 'app_ui/newPassword.html')
