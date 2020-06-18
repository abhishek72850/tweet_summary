from datetime import datetime

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from subscriber.models import SubscribeModel
from .helpers import decode_token, generate_token, add_subscriber, send_subscription_email, confirm_email_verification, \
    unsubscribe


class UpsertSubscriber(APIView):

    def post(self, request, format=None):

        current_datetime = datetime.now()

        if 'subscriber_email' in request.POST.keys():

            start_date = datetime.strptime(request.POST['subscription_start_date'], '%Y-%m-%d')
            end_date = datetime.strptime(request.POST['subscription_end_date'], '%Y-%m-%d')

            if current_datetime.date() > start_date.date():
                return Response({'status': status.HTTP_400_BAD_REQUEST,
                                 'data': 'Subscription start date cannot be less than current date'})
            elif start_date > end_date:
                return Response({'status': status.HTTP_400_BAD_REQUEST,
                                 'data': 'Subscription start date cannot be greater than end date'})

            response, status_msg = add_subscriber(
                request.POST['subscriber_email'], request.POST['subscriber_topic'],
                start_date, end_date)

            if isinstance(response, SubscribeModel):
                if not response.email_verified:
                    token = generate_token(response.email, response.id)
                    confirmation_url = 'https://tweet-summary.herokuapp.com/subscriber/confirm_email?verification_code={}'.format(token)
                    send_subscription_email(response, confirmation_url)
                if status_msg == 'CREATED':
                    return Response({
                        'status': status.HTTP_200_OK,
                        'data': 'Subscription created, please check email to verify'
                    })
                else:
                    return Response({
                        'status': status.HTTP_200_OK,
                        'data': 'Subscription updated'
                    })

        return Response({'status': status.HTTP_400_BAD_REQUEST, 'data': 'Something went wrong!!'})


class ConfirmSubscription(APIView):

    def get(self, request, format=None):

        if 'verification_code' in request.GET.keys():
            token = request.GET['verification_code']

            success, payload = decode_token(token)

            if success:
                subscriber_id = payload['subscriber_id']
                email = payload['email']

                if confirm_email_verification(email, subscriber_id):
                    return Response({'status': status.HTTP_200_OK, 'data': 'Email verified successfully'})

        return Response({'status': status.HTTP_400_BAD_REQUEST, 'data': 'Link expired!!'})


class UnSubscribe(APIView):

    def get(self, request, format=None):
        if 'verification_code' in request.GET.keys():
            token = request.GET['verification_code']

            success, payload = decode_token(token)

            if success:
                subscriber_id = payload['subscriber_id']
                email = payload['email']

                if unsubscribe(email, subscriber_id):
                    return Response({'status': status.HTTP_200_OK, 'data': 'Unsubscribed successfully'})

        return Response({'status': status.HTTP_400_BAD_REQUEST, 'data': 'Something went wrong!!'})
