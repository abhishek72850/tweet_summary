from django.http import Http404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from datetime import datetime, timedelta

from django.contrib.auth import login

from helpers.auths import is_action_allowed, generate_token, decode_token
from helpers.emails import send_email_verification_link, send_subscription_verification_link, send_password_reset_link
from helpers.twitter import TwitterHelper
from helpers.utils import request_contain_keys, get_host_origin, get_utc_now, get_local_datetime
from helpers.db import get_account_details, get_plan_by_id, add_plan_request, update_quick_analysis_counter, \
    add_subscription, get_user_by_email, update_user_password, confirm_subscription, confirm_email_verification, \
    unsubscribe, remove_subscription

from app_perf.forms import CustomUserLoginForm, CustomUserRegisterForm
from app_perf.auths import CustomUserAuthentication
from app_perf.models import SubscriptionModel

from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django.views.decorators.vary import vary_on_cookie


# Create your views here.


class AccountLogin(APIView):
    def post(self, request, format=None):
        if request_contain_keys(request.POST, ['user_email', 'user_password']):
            form_data = {
                'email': request.POST['user_email'],
                'password': request.POST['user_password']
            }

            form = CustomUserLoginForm(form_data)

            # is_valid return true if user not in db
            if not form.is_valid():
                user = CustomUserAuthentication().authenticate(request, email=form_data['email'],
                                                               password=form_data['password'])
                if user is not None:
                    if not user.email_verified:
                        return Response(data={'data': 'Email is not verified yet'}, status=status.HTTP_400_BAD_REQUEST)
                    if user.status == 'SUSPENDED':
                        return Response(data={'data': 'Your account is suspended'}, status=status.HTTP_400_BAD_REQUEST)

                    login(request, user, backend='app_perf.auths.CustomUserAuthentication')
                    return Response(data={'data': user.toJSON()}, status=status.HTTP_200_OK)
            else:
                return Response(data={'data': 'User not found'}, status=status.HTTP_401_UNAUTHORIZED)

        return Response(data={'data': 'Invalid User credentials'}, status=status.HTTP_400_BAD_REQUEST)


class AccountRegister(APIView):
    def post(self, request, format=None):
        if request_contain_keys(request.POST, ['user_email', 'user_password', 'user_cnf_password']):
            if request.POST['user_password'] != request.POST['user_cnf_password']:
                return Response(data={'data': 'Password authentication failed'}, status=status.HTTP_400_BAD_REQUEST)

            form_data = {
                'email': request.POST['user_email'],
                'password': request.POST['user_password'],
                'timezone_offset': request.POST.get('timezone_offset')
            }

            form = CustomUserRegisterForm(form_data)

            if form.is_valid():
                user = form.save()
                if user is not None:
                    token = generate_token(email=user.email, user_id=user.id)
                    email_verification_url = '{}/api/account/confirm_email?verification_code={}'.format(
                        get_host_origin(request), token)
                    send_email_verification_link(user, email_verification_url)
                    return Response(data={'data': user.toJSON()}, status=status.HTTP_200_OK)
                else:
                    return Response(data={'data': 'User not found'}, status=status.HTTP_401_UNAUTHORIZED)
            else:
                return Response(data={'data': 'User already exist'}, status=status.HTTP_400_BAD_REQUEST)

        return Response(data={'data': 'Invalid User credentials'}, status=status.HTTP_400_BAD_REQUEST)


class AccountDetails(APIView):
    def get(self, request, format=None):
        if not request.user.is_authenticated:
            return Response(data={'data': 'Authentication Failed, Please login'}, status=status.HTTP_401_UNAUTHORIZED)

        details = get_account_details(request.user.id)
        if len(details) > 0:
            return Response(data={'data': details}, status=status.HTTP_200_OK)

        return Response(status=status.HTTP_400_BAD_REQUEST, data={'data': 'Something went wrong!!'})

    def post(self, request, format=None):
        if not request.user.is_authenticated:
            return Response(data={'data': 'Authentication Failed, Please login'}, status=status.HTTP_401_UNAUTHORIZED)

        if request_contain_keys(request.POST, ['subscription_ids[]']):
            for id in request.POST.getlist('subscription_ids[]'):
                remove_subscription(request.user, id)

            return Response(data={'data':'Subscriptions removed successfully'}, status=status.HTTP_200_OK)

        return Response(data={'data': 'Invalid Parameters'}, status=status.HTTP_400_BAD_REQUEST)


class AccountAssignOrUpdatePlan(APIView):
    def post(self, request, format=None):
        if not request.user.is_authenticated:
            return Response(data={'data': 'Authentication Failed, Please login'}, status=status.HTTP_401_UNAUTHORIZED)

        if request_contain_keys(request.POST, ['plan_id']):
            print(request.POST)
            plan_set = get_plan_by_id(request.POST['plan_id'][0])
            if len(plan_set) > 0:
                add_plan_request(request.user, plan_set[0])
                return Response(data={'data': 'Plan request added successfully'}, status=status.HTTP_200_OK)
            else:
                return Response(data={'data': 'Invalid Plan'}, status=status.HTTP_400_BAD_REQUEST)

        return Response(data={'data': 'Invalid Parameters'}, status=status.HTTP_400_BAD_REQUEST)


class AccountSubscribeTopic(APIView):
    def post(self, request, format=None):
        if not request.user.is_authenticated:
            return Response(data={'data': 'Authentication Failed, Please login'}, status=status.HTTP_401_UNAUTHORIZED)

        if request_contain_keys(request.POST, ['subscribe_start_date', 'subscribe_end_date', 'search_topic']):

            current_datetime = get_local_datetime(request.user.timezone_offset)

            start_date = datetime.strptime(request.POST['subscribe_start_date'], '%Y-%m-%d')
            end_date = datetime.strptime(request.POST['subscribe_end_date'], '%Y-%m-%d')

            if current_datetime.date() > start_date.date():
                return Response(status=status.HTTP_400_BAD_REQUEST,
                                data={'data': 'Subscription start date cannot be less than current date'})
            elif start_date > end_date:
                return Response(status=status.HTTP_400_BAD_REQUEST,
                                data={'data': 'Subscription start date cannot be greater than end date'})

            if (end_date - start_date).days > request.user.plan_subscribed.subscription_period_max_days:
                return Response(
                    status=status.HTTP_400_BAD_REQUEST,
                    data={'data': 'Subscription period exceeded select plan {} days limit!!'.format(
                        request.user.plan_subscribed.subscription_period_max_days)
                          })

            response = is_action_allowed(request.user)

            if response is True:
                subscription, status_msg = add_subscription(request.user, request.POST['search_topic'],
                                                            start_date, end_date)
            else:
                return Response(data={'data': response}, status=status.HTTP_400_BAD_REQUEST)

            if isinstance(subscription, SubscriptionModel):
                if subscription.subscription_status == 'IDLE':
                    token = generate_token(email=subscription.user.email, subscription_id=subscription.id)
                    confirmation_url = '{}/api/account/confirm_subscription?verification_code={}'.format(
                        get_host_origin(request), token)
                    send_subscription_verification_link(subscription, confirmation_url)
                if status_msg == 'CREATED':
                    return Response(
                        status=status.HTTP_200_OK,
                        data={'data': 'Subscription created, please check email to verify'}
                    )
                elif status_msg == 'UPDATED':
                    return Response(
                        status=status.HTTP_200_OK,
                        data={'data': 'Subscription updated'}
                    )
            else:
                if status_msg == 'NOT_VERIFIED':
                    return Response(
                        status=status.HTTP_400_BAD_REQUEST,
                        data={'data': 'Email is not verified!!'}
                    )
                if status_msg == 'QUOTA_EXHAUSTED':
                    return Response(
                        status=status.HTTP_400_BAD_REQUEST,
                        data={'data': 'You have reached your ACTIVE subscriptions quota!!'}
                    )

        return Response(status=status.HTTP_400_BAD_REQUEST, data={'data': 'Something went wrong!!'})


class AccountChangePassword(APIView):
    def post(self, request, format=None):
        if not request.user.is_authenticated:
            return Response(data={'data': 'Authentication Failed, Please login'}, status=status.HTTP_401_UNAUTHORIZED)

        if request_contain_keys(request.POST, ['current_password', 'new_password', 'confirm_password']):
            if request.POST['new_password'] != request.POST['confirm_password']:
                return Response(status=status.HTTP_400_BAD_REQUEST, data={'data': 'Password authentication failed'})

            if update_user_password(request.user.id, request.POST['new_password']) == 1:
                return Response(status=status.HTTP_200_OK, data={'data': 'Password changed successfully!!'})
            else:
                return Response(status=status.HTTP_404_NOT_FOUND, data={'data': 'Something went wrong, code CNSU4'})

        return Response(status=status.HTTP_400_BAD_REQUEST, data={'data': 'Invalid Parameters!!'})


class GeneratePasswordResetLink(APIView):
    def post(self, request, format=None):
        if request_contain_keys(request.POST, ['user_email']):
            user_set = get_user_by_email(request.POST['user_email'])

            if len(user_set) > 0:
                token = generate_token(email=user_set[0].email, expire=1, user_id=user_set[0].id)
                password_reset_url = '{}/app/reset_password?verification_code={}'.format(get_host_origin(request),
                                                                                         token)
                send_password_reset_link(user_set[0], password_reset_url)
                return Response(status=status.HTTP_200_OK,
                                data={'data': 'Please check your mail for password reset link'})
            else:
                return Response(status=status.HTTP_400_BAD_REQUEST, data={'data': 'Email is not registered!!'})
        return Response(status=status.HTTP_400_BAD_REQUEST, data={'data': 'Invalid Parameters!!'})


class ResetPassword(APIView):
    def post(self, request, format=None):
        if request_contain_keys(request.POST, ['verification_code', 'new_password', 'confirm_password']):
            if request.POST['new_password'] != request.POST['confirm_password']:
                return Response(status=status.HTTP_400_BAD_REQUEST, data={'data': 'Password authentication failed'})

            success, payload = decode_token(request.POST['verification_code'])

            if success:
                email = payload['email']
                user_id = payload['user_id']

                if update_user_password(user_id, request.POST['new_password']) == 1:
                    return Response(status=status.HTTP_200_OK, data={'data': 'Password reset successful!!'})
                else:
                    return Response(status=status.HTTP_404_NOT_FOUND, data={'data': 'Something went wrong, code CNSU3'})
            else:
                return Response(status=status.HTTP_403_FORBIDDEN, data={'data': 'Token authentication failed'})

        return Response(status=status.HTTP_400_BAD_REQUEST, data={'data': 'Invalid Parameters!!'})


class ConfirmEmail(APIView):
    def get(self, request, format=None):
        if request_contain_keys(request.GET, ['verification_code']):
            token = request.GET['verification_code']

            success, payload = decode_token(token)

            print(payload)

            if success:
                user_id = payload['user_id']
                email = payload['email']

                if confirm_email_verification(email, user_id):
                    return Response({'status': status.HTTP_200_OK, 'data': 'Email verified successfully'})

        return Response({'status': status.HTTP_400_BAD_REQUEST, 'data': 'Link expired!!'})


class ConfirmSubscription(APIView):
    def get(self, request, format=None):
        if request_contain_keys(request.GET, ['verification_code']):
            token = request.GET['verification_code']

            success, payload = decode_token(token)

            if success:
                subscription_id = payload['subscription_id']
                email = payload['email']

                if confirm_subscription(email, subscription_id):
                    return Response({'status': status.HTTP_200_OK, 'data': 'Subscription verified successfully'})

        return Response({'status': status.HTTP_400_BAD_REQUEST, 'data': 'Link expired!!'})


class UnSubscribe(APIView):
    def get(self, request, format=None):
        if request_contain_keys(request.GET, ['verification_code']):
            token = request.GET['verification_code']

            success, payload = decode_token(token)

            if success:
                subscription_id = payload['subscription_id']
                email = payload['email']

                if unsubscribe(email, subscription_id):
                    return Response(status=status.HTTP_200_OK, data={'data': 'Unsubscribed successfully'})

        return Response(status=status.HTTP_400_BAD_REQUEST, data={'data': 'Something went wrong!!'})


class SummaryAnalysis(APIView):

    @method_decorator(cache_page(60 * 60 * 2))
    @method_decorator(vary_on_cookie)
    def get(self, request, format=None):
        if not request.user.is_authenticated:
            return Response(data={'data': 'Authentication Failed, Please login'}, status=status.HTTP_401_UNAUTHORIZED)

        if request_contain_keys(request.GET, ['query']):

            response = is_action_allowed(request.user)

            if response is True:
                if request.user.quick_analysis_counter < request.user.plan_subscribed.quick_analysis_quota:
                    tweet = TwitterHelper(request.GET['query'])
                    data = tweet.fetch_analysis()

                    if update_quick_analysis_counter(request.user) == 1:
                        return Response(data={'data': data}, status=status.HTTP_200_OK)
                    else:
                        return Response(data={'data': 'Something went wrong, code:CNSU1'},
                                        status=status.HTTP_500_INTERNAL_SERVER_ERROR)
                else:
                    return Response(data={'data': 'You have exhausted your quick analysis quota'},
                                    status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response(data={'data': response}, status=status.HTTP_400_BAD_REQUEST)

        return Response(data={'data': 'Invalid or missing Parameters'}, status=status.HTTP_400_BAD_REQUEST)
