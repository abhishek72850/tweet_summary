from datetime import datetime

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from subscriber.models import SubscribeModel
from .helpers import decode_token, generate_token, add_subscription, send_email_verification_link, \
    send_subscription_verification_link, confirm_email_verification, confirm_subscription, unsubscribe, \
    register_or_verify_subscriber, \
    get_subscription_and_profile_details, remove_subscription, update_subscription_details, get_user_details


class RegisterUser(APIView):
    def post(self, request, format=None):
        if 'subscriber_email' in request.POST.keys() and 'subscriber_password' in request.POST.keys():
            user = register_or_verify_subscriber(request.POST['subscriber_email'], request.POST['subscriber_password'],
                                                 request.POST['subscriber_plan'])
            print(user)
            if user is not None:
                if not user.email_verified:
                    token = generate_token(email=user.email, user_id=user.id)
                    email_verification_url = 'https://tweet-summary.herokuapp.com/subscriber/confirm_email?verification_code={}'.format(
                        token)
                    send_email_verification_link(user, email_verification_url)

                return Response({
                    'status': status.HTTP_200_OK,
                    'data': 'User registered, please check email to verify'
                })
        return Response({'status': status.HTTP_400_BAD_REQUEST, 'data': 'Something went wrong!!'})


class UpsertSubscription(APIView):

    def post(self, request, format=None):

        current_datetime = datetime.now()

        if 'subscriber_email' in request.POST.keys() and 'subscriber_password' in request.POST.keys():

            start_date = datetime.strptime(request.POST['subscription_start_date'], '%Y-%m-%d')
            end_date = datetime.strptime(request.POST['subscription_end_date'], '%Y-%m-%d')

            if current_datetime.date() > start_date.date():
                return Response({'status': status.HTTP_400_BAD_REQUEST,
                                 'data': 'Subscription start date cannot be less than current date'})
            elif start_date > end_date:
                return Response({'status': status.HTTP_400_BAD_REQUEST,
                                 'data': 'Subscription start date cannot be greater than end date'})

            subscription, status_msg = add_subscription(request.POST['subscriber_email'],
                                                        request.POST['subscriber_password'],
                                                        request.POST['subscriber_topic'],
                                                        start_date, end_date)

            if isinstance(subscription, SubscribeModel):
                if subscription.subscription_status == 'IDLE':
                    token = generate_token(email=subscription.user.email, subscription_id=subscription.id)
                    confirmation_url = 'https://tweet-summary.herokuapp.com/subscriber/confirm_subscription?verification_code={}'.format(
                        token)
                    send_subscription_verification_link(subscription, confirmation_url)
                if status_msg == 'CREATED':
                    return Response({
                        'status': status.HTTP_200_OK,
                        'data': 'Subscription created, please check email to verify'
                    })
                elif status_msg == 'UPDATED':
                    return Response({
                        'status': status.HTTP_200_OK,
                        'data': 'Subscription updated'
                    })
            else:
                if status_msg == 'NOT_REGISTERED':
                    return Response({
                        'status': status.HTTP_400_BAD_REQUEST,
                        'data': 'Email not registered or not verified!!'
                    })
                elif status_msg == 'QUOTA_EXHAUSTED':
                    return Response({
                        'status': status.HTTP_400_BAD_REQUEST,
                        'data': 'You have reached your ACTIVE subscriptions quota!!'
                    })

        return Response({'status': status.HTTP_400_BAD_REQUEST, 'data': 'Something went wrong!!'})


class ViewOrUpdateUserAllDetails(APIView):
    def get(self, request, format=None):
        if 'subscriber_email' in request.GET.keys() and 'subscriber_password' in request.GET.keys():
            details = get_subscription_and_profile_details(request.GET['subscriber_email'],
                                                           request.GET['subscriber_password'])
            print(details)
            if len(details) > 0:
                return Response({
                    'status': status.HTTP_200_OK,
                    'data': details
                })

        return Response({'status': status.HTTP_400_BAD_REQUEST, 'data': 'Something went wrong!!'})

    def post(self, request, format=None):
        if 'subscriber_email' in request.POST.keys() and 'subscriber_password' in request.POST.keys():
            user_set = get_user_details(request.POST['subscriber_email'], request.POST['subscriber_password'])

            if len(user_set) > 0:
                for id in request.POST.getlist('subscription_ids[]'):
                    if not remove_subscription(request.POST['subscriber_email'], request.POST['subscriber_password'],
                                               id):
                        break

                if user_set[0].plan_subscribed.id != int(request.POST['subscriber_plan']):
                    return Response(
                        {'status': status.HTTP_400_BAD_REQUEST, 'data': 'Plan updation service will come soon'})

                return Response({
                    'status': status.HTTP_200_OK,
                    'data': 'Details Updated Successfully!!!'
                })

        return Response({'status': status.HTTP_400_BAD_REQUEST, 'data': 'Something went wrong!!'})


class ConfirmEmail(APIView):
    def get(self, request, format=None):

        if 'verification_code' in request.GET.keys():
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

        if 'verification_code' in request.GET.keys():
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
        if 'verification_code' in request.GET.keys():
            token = request.GET['verification_code']

            success, payload = decode_token(token)

            if success:
                subscription_id = payload['subscription_id']
                email = payload['email']

                if unsubscribe(email, subscription_id):
                    return Response({'status': status.HTTP_200_OK, 'data': 'Unsubscribed successfully'})

        return Response({'status': status.HTTP_400_BAD_REQUEST, 'data': 'Something went wrong!!'})
