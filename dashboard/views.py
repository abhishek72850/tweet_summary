from django.shortcuts import render

# Create your views here.


def dashboard(request):
    return render(request, 'dashboard/index.html')


def choice_panel(request):
    return render(request, 'dashboard/panel.html')


def choice_portal(request):
    return render(request, 'dashboard/portal.html')
