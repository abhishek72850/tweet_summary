from django.contrib import admin
from django.urls import path, include
from . import views

urlpatterns = [
    path('login', views.LoginView, name='login'),
    path('logout', views.LogoutView, name='logout'),
    path('dashboard', views.DashboardView, name='dashboard'),
    path('manage_users', views.ManageUsersView, name='manage_users'),
    path('manage_subscriptions', views.ManageSubscriptionsView, name='manage_subscriptions'),
    path('update_user', views.UpdateUserView, name='update_user'),
    path('update_subscription', views.UpdateSubscriptionView, name='update_subscription'),
    path('assign_test_plan', views.AssignTestPlanView, name='assign_test_plan'),
    path('plan_request_change', views.PlanChangeRequestView, name='plan_request_change'),
    path('upcoming_plan', views.UpcomingUserPlansView, name='upcoming_plan'),
    path('assign', views.RegisterTestUser.as_view()),
    path('all_users', views.GetAllUsers.as_view()),
    path('all_subscriptions', views.GetAllSubscriptions.as_view()),
    path('get_user', views.GetUser.as_view()),
    path('update_user_status', views.UpdateUser.as_view()),
    path('get_subscription', views.GetSubscription.as_view()),
    path('update_subscription_status', views.UpdateSubscription.as_view()),
    path('send_user_verification', views.SendUserVerificationLink.as_view()),
    path('send_subscription_verification', views.SendSubscriptionVerificationLink.as_view()),
    path('get_all_requests', views.GetAllPlanChangeRequests.as_view()),
    path('accept_requests', views.AcceptPlanChangeRequest.as_view()),
    path('decline_requests', views.DeclinePlanChangeRequest.as_view()),
    path('renew_plan', views.RenewUserPlan.as_view()),
    path('get_all_upcoming_user_plans', views.GetAllUpcomingUserPlans.as_view()),
]