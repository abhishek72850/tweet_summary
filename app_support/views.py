from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.shortcuts import render, redirect
from django.core.serializers import serialize
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

import json

from app_perf.models import Admins, Subscribers

from subscriber.models import SubscribeModel

from helpers.auths import generate_token
from helpers.emails import send_email_verification_link, send_subscription_verification_link, \
    send_plan_change_confirmation
from helpers.db import register_or_verify_subscriber, get_user_details, get_all_users, get_all_subscriptions, \
    get_user_by_id, get_subscription_by_id, update_user_status, \
    update_subscription_status, get_all_plan_change_requests, \
    get_plan_request_by_id, update_plan_request_status, update_user_plan, \
    get_all_upcoming_user_plans, is_user_plan_expired, add_upcoming_plan

from fuzzywuzzy import fuzz


# Create your views here.


def LoginView(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        print(username, password)
        user = authenticate(request, email=username, password=password)
        if user is not None:
            login(request, user)
            return redirect("dashboard")
    return render(request, 'app_support/login.html', {})


def LogoutView(request):
    logout(request)
    return redirect('login')


def DashboardView(request):
    if not request.user.is_authenticated:
        return redirect('login')
        # username = request.session['username']
    details = Admins.objects.get(email=request.user.email)
    return render(request, 'app_support/dashboard.html', {"details": details})


def ManageUsersView(request):
    if not request.user.is_authenticated:
        return redirect('login')
        # username = request.session['username']
    details = Admins.objects.get(email=request.user.email)
    return render(request, 'app_support/manage_users.html', {"details": details})


def ManageSubscriptionsView(request):
    if not request.user.is_authenticated:
        return redirect('login')
        # username = request.session['username']
    details = Admins.objects.get(email=request.user.email)
    return render(request, 'app_support/manage_subscriptions.html', {"details": details})


def UpdateUserView(request):
    if not request.user.is_authenticated:
        return redirect('login')
        # username = request.session['username']
    details = Admins.objects.get(email=request.user.email)
    return render(request, 'app_support/update_user.html', {"details": details})


def UpdateSubscriptionView(request):
    if not request.user.is_authenticated:
        return redirect('login')
        # username = request.session['username']
    details = Admins.objects.get(email=request.user.email)
    return render(request, 'app_support/update_subscription.html', {"details": details})


def AssignTestPlanView(request):
    if not request.user.is_authenticated:
        return redirect('login')
        # username = request.session['username']
    details = Admins.objects.get(email=request.user.email)
    return render(request, 'app_support/assign_test_plan.html', {"details": details})


def PlanChangeRequestView(request):
    if not request.user.is_authenticated:
        return redirect('login')
        # username = request.session['username']
    details = Admins.objects.get(email=request.user.email)
    return render(request, 'app_support/plan_change_request.html', {"details": details})


def UpcomingUserPlansView(request):
    if not request.user.is_authenticated:
        return redirect('login')
        # username = request.session['username']
    details = Admins.objects.get(email=request.user.email)
    return render(request, 'app_support/upcoming_user_plans.html', {"details": details})


class RegisterTestUser(APIView):
    def post(self, request, format=None):
        if not request.user.is_authenticated:
            return Response(data={'data': 'Authentication Failed'}, status=status.HTTP_401_UNAUTHORIZED)
        if 'test_user_email' in request.POST.keys() and 'test_user_password' in request.POST.keys() and 'test_user_cnf_password' in request.POST.keys():
            if request.POST['test_user_password'].strip() != request.POST['test_user_cnf_password'].strip():
                return Response(status=status.HTTP_400_BAD_REQUEST, data={'data': 'Password Authentication failed!!'})
            result = get_user_details(request.POST['test_user_email'], request.POST['test_user_password'])

            if len(result) == 0:
                user = register_or_verify_subscriber(request.POST['test_user_email'],
                                                     request.POST['test_user_password'],
                                                     '4')
                if not user.email_verified:
                    token = generate_token(email=user.email, user_id=user.id)
                    email_verification_url = 'https://tweet-summary.herokuapp.com/subscriber/confirm_email?verification_code={}'.format(
                        token)
                    send_email_verification_link(user, email_verification_url)

                return Response(
                    status=status.HTTP_200_OK,
                    data={'data': 'User registered, please check email to verify'}
                )
            else:
                return Response(status=status.HTTP_400_BAD_REQUEST, data={'data': 'User already exist!!'})
        return Response(status=status.HTTP_400_BAD_REQUEST, data={'data': 'Invalid parameters!!'})


class GetAllUsers(APIView):
    def get(self, request, format=None):
        if not request.user.is_authenticated:
            return Response(data={'data': 'Authentication Failed'}, status=status.HTTP_401_UNAUTHORIZED)

        user_list = []

        if request.GET.get('search_by_email', False) != '':
            for user in get_all_users():
                if fuzz.ratio(request.GET['search_by_email'], user.email) > 20:
                    user_list.append(user)
            user_list = serialize('json', user_list)
        else:
            user_list = serialize('json', get_all_users())

        return Response(data={'data': user_list}, status=status.HTTP_200_OK)


class GetUser(APIView):
    def get(self, request, format=None):
        if not request.user.is_authenticated:
            return Response(data={'data': 'Authentication Failed'}, status=status.HTTP_401_UNAUTHORIZED)

        if 'user_id' in request.GET.keys():
            user_set = get_user_by_id(request.GET['user_id'])

            if len(user_set) > 0:
                total_subscriptions = len(SubscribeModel.objects.filter(user=user_set[0]))
                return Response(data={
                    'data': {
                        'user': user_set[0].toJSON(),
                        'plan': user_set[0].plan_subscribed.toJSON(),
                        'subscriptions': total_subscriptions
                    }
                }, status=status.HTTP_200_OK)

            return Response(status=status.HTTP_400_BAD_REQUEST, data={'data': 'User not found!!'})

        return Response(status=status.HTTP_400_BAD_REQUEST, data={'data': 'Invalid parameters!!'})


class UpdateUser(APIView):
    def post(self, request, format=None):
        if not request.user.is_authenticated:
            return Response(data={'data': 'Authentication Failed'}, status=status.HTTP_401_UNAUTHORIZED)

        if 'user_id' in request.POST.keys() and 'status' in request.POST.keys():
            if request.POST['status'] in ['PENDING_VERIFICATION', 'VERIFIED', 'SUSPENDED']:
                if update_user_status(request.POST['user_id'], request.POST['status']) == 1:
                    return Response(status=status.HTTP_200_OK, data={'data': 'User status updated successfully!!'})
                else:
                    return Response(status=status.HTTP_400_BAD_REQUEST,
                                    data={'data': 'User is not valid, unable to update status!!'})

            return Response(status=status.HTTP_400_BAD_REQUEST, data={'data': 'Invalid status input!!'})

        return Response(status=status.HTTP_400_BAD_REQUEST, data={'data': 'Invalid parameters!!'})


class UpdateSubscription(APIView):
    def post(self, request, format=None):
        if not request.user.is_authenticated:
            return Response(data={'data': 'Authentication Failed'}, status=status.HTTP_401_UNAUTHORIZED)

        if 'subscription_id' in request.POST.keys() and 'status' in request.POST.keys():
            if request.POST['status'] in ['IDLE', 'ACTIVE', 'SUSPENDED']:
                if update_subscription_status(request.POST['subscription_id'], request.POST['status']) == 1:
                    return Response(status=status.HTTP_200_OK,
                                    data={'data': 'Subscription status updated successfully!!'})
                else:
                    return Response(status=status.HTTP_400_BAD_REQUEST,
                                    data={'data': 'Subscription is not valid, unable to update status!!'})

            return Response(status=status.HTTP_400_BAD_REQUEST, data={'data': 'Invalid status input!!'})

        return Response(status=status.HTTP_400_BAD_REQUEST, data={'data': 'Invalid parameters!!'})


class GetAllSubscriptions(APIView):
    def get(self, request, format=None):
        if not request.user.is_authenticated:
            return Response(data={'data': 'Authentication Failed'}, status=status.HTTP_401_UNAUTHORIZED)

        subscription_list = []

        if request.GET.get('search_by_email', False) != '':
            for subscription in get_all_subscriptions():
                if fuzz.ratio(request.GET['search_by_email'], subscription.user.email) > 20:
                    subscription_list.append([subscription.user.toJSON(), subscription.toJSON()])
        else:
            for subscription in get_all_subscriptions():
                subscription_list.append([subscription.user.toJSON(), subscription.toJSON()])

        return Response(data={'data': subscription_list}, status=status.HTTP_200_OK)


class GetSubscription(APIView):
    def get(self, request, format=None):
        if not request.user.is_authenticated:
            return Response(data={'data': 'Authentication Failed'}, status=status.HTTP_401_UNAUTHORIZED)

        if 'subscription_id' in request.GET.keys():
            subscription_set = get_subscription_by_id(request.GET['subscription_id'])

            if len(subscription_set) > 0:
                return Response(data={
                    'data': {
                        'subscription': subscription_set[0].toJSON(),
                        'user': subscription_set[0].user.toJSON(),
                        'plan': subscription_set[0].user.plan_subscribed.toJSON()
                    }
                }, status=status.HTTP_200_OK)

            return Response(status=status.HTTP_400_BAD_REQUEST, data={'data': 'Subscription not found!!'})

        return Response(status=status.HTTP_400_BAD_REQUEST, data={'data': 'Invalid parameters!!'})


class SendUserVerificationLink(APIView):
    def post(self, request, format=None):
        if not request.user.is_authenticated:
            return Response(data={'data': 'Authentication Failed'}, status=status.HTTP_401_UNAUTHORIZED)

        if 'user_id' in request.POST.keys():
            user_set = get_user_by_id(request.POST['user_id'])

            if len(user_set) > 0:
                token = generate_token(email=user_set[0].email, user_id=user_set[0].id)
                email_verification_url = 'https://tweet-summary.herokuapp.com/subscriber/confirm_email?verification_code={}'.format(
                    token)
                send_email_verification_link(user_set[0], email_verification_url)

                return Response(
                    status=status.HTTP_200_OK,
                    data={'data': 'User verification mail sent!!'}
                )

            return Response(status=status.HTTP_400_BAD_REQUEST, data={'data': 'User not found!!'})

        return Response(status=status.HTTP_400_BAD_REQUEST, data={'data': 'Invalid parameters!!'})


class SendSubscriptionVerificationLink(APIView):
    def post(self, request, format=None):
        if not request.user.is_authenticated:
            return Response(data={'data': 'Authentication Failed'}, status=status.HTTP_401_UNAUTHORIZED)

        if 'subscription_id' in request.POST.keys():
            subscription_set = get_subscription_by_id(request.POST['subscription_id'])

            if len(subscription_set) > 0:
                if subscription_set[0].user.email_verified:
                    token = generate_token(email=subscription_set[0].user.email, subscription_id=subscription_set[0].id)
                    confirmation_url = 'https://tweet-summary.herokuapp.com/subscriber/confirm_subscription?verification_code={}'.format(
                        token)
                    send_subscription_verification_link(subscription_set[0], confirmation_url)

                    return Response(
                        status=status.HTTP_200_OK,
                        data={'data': 'Subscription verification mail sent!!'}
                    )
                return Response(status=status.HTTP_400_BAD_REQUEST, data={'data': 'User not Verified!!'})

            return Response(status=status.HTTP_400_BAD_REQUEST, data={'data': 'Subscription not found!!'})

        return Response(status=status.HTTP_400_BAD_REQUEST, data={'data': 'Invalid parameters!!'})


class GetAllUpcomingUserPlans(APIView):
    def get(self, request, format=None):
        if not request.user.is_authenticated:
            return Response(data={'data': 'Authentication Failed'}, status=status.HTTP_401_UNAUTHORIZED)

        upcoming_plan_list = []

        if request.GET.get('search_by_email', False) != '':
            for upcoming_plan in get_all_upcoming_user_plans():
                if fuzz.ratio(request.GET['search_by_email'], upcoming_plan.user.email) > 20:
                    upcoming_plan_list.append(
                        [upcoming_plan.user.toJSON(), upcoming_plan.toJSON(), upcoming_plan.plan.toJSON()])
        else:
            for upcoming_plan in get_all_upcoming_user_plans():
                upcoming_plan_list.append(
                    [upcoming_plan.user.toJSON(), upcoming_plan.toJSON(), upcoming_plan.plan.toJSON()])

        return Response(data={'data': upcoming_plan_list}, status=status.HTTP_200_OK)


class GetAllPlanChangeRequests(APIView):
    def get(self, request, format=None):
        if not request.user.is_authenticated:
            return Response(data={'data': 'Authentication Failed'}, status=status.HTTP_401_UNAUTHORIZED)

        request_list = []

        if request.GET.get('search_by_email', False) != '':
            for plan_request in get_all_plan_change_requests():
                if fuzz.ratio(request.GET['search_by_email'], plan_request.user.email) > 20:
                    old_plan = plan_request.old_plan.toJSON() if plan_request.old_plan is not None else None
                    request_list.append(
                        [plan_request.user.toJSON(), plan_request.toJSON(), old_plan,
                         plan_request.new_plan.toJSON()])
        else:
            for plan_request in get_all_plan_change_requests():
                old_plan = plan_request.old_plan.toJSON() if plan_request.old_plan is not None else None
                request_list.append([plan_request.user.toJSON(), plan_request.toJSON(), old_plan,
                                     plan_request.new_plan.toJSON()])

        return Response(data={'data': request_list}, status=status.HTTP_200_OK)


class AcceptPlanChangeRequest(APIView):
    def post(self, request, format=None):
        if not request.user.is_authenticated:
            return Response(data={'data': 'Authentication Failed'}, status=status.HTTP_401_UNAUTHORIZED)

        if 'plan_request_id' in request.POST.keys():
            plan_request = get_plan_request_by_id(request.POST['plan_request_id'])
            update_plan = False
            if len(plan_request) > 0:
                if update_plan_request_status(plan_request[0].id, 'ACCEPTED') == 1:
                    if plan_request[0].user.plan_subscribed is not None:
                        if is_user_plan_expired(plan_request[0].user):
                            update_plan = True
                        else:
                            add_upcoming_plan(plan_request[0].user, plan_request[0].new_plan)
                            return Response(data={'data': 'Plan added to upcoming list'}, status=status.HTTP_200_OK)
                    else:
                        update_plan = True
                else:
                    return Response(data={'data': 'Something went wrong, code: CNSU3'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
                if update_plan:
                    if update_user_plan(plan_request[0].user, plan_request[0].new_plan) == 1:
                        send_plan_change_confirmation(plan_request[0])
                        return Response(data={'data': 'Plan changed successfully'}, status=status.HTTP_200_OK)
                    else:
                        return Response(data={'data': 'Something went wrong, code: CNSU2'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


                return Response(data={'data': 'Unable to change plan'}, status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response(data={'data': 'Plan is invalid'}, status=status.HTTP_400_BAD_REQUEST)

        return Response(data={'data': 'Invalid parameters'}, status=status.HTTP_400_BAD_REQUEST)


class DeclinePlanChangeRequest(APIView):
    def post(self, request, format=None):
        if not request.user.is_authenticated:
            return Response(data={'data': 'Authentication Failed'}, status=status.HTTP_401_UNAUTHORIZED)

        if 'plan_request_id' in request.POST.keys():
            plan_request = get_plan_request_by_id(request.POST['plan_request_id'])

            if len(plan_request) > 0:
                if update_plan_request_status(plan_request[0].id, 'DECLINED') == 1:
                    return Response(data={'data': 'Plan changed request declined'}, status=status.HTTP_200_OK)

                return Response(data={'data': 'Unable to decline, something went wrong'},
                                status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response(data={'data': 'Plan is invalid'}, status=status.HTTP_400_BAD_REQUEST)

        return Response(data={'data': 'Invalid parameters'}, status=status.HTTP_400_BAD_REQUEST)


class RenewUserPlan(APIView):
    def post(self, request, format=None):
        if not request.user.is_authenticated:
            return Response(data={'data': 'Authentication Failed'}, status=status.HTTP_401_UNAUTHORIZED)

        if 'user_id' in request.POST.keys():
            user_set = get_user_by_id(request.POST['user_id'])

            if len(user_set) > 0:
                pass
            else:
                return Response(data={'data': 'User not found'}, status=status.HTTP_400_BAD_REQUEST)
        return Response(data={'data': 'Invalid parameters'}, status=status.HTTP_400_BAD_REQUEST)
