from django.http import Http404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from . import utils, helpers
from subscriber.helpers import get_user_details
from subscriber.models import UserModel

from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django.views.decorators.vary import vary_on_cookie


# Create your views here.


class SummaryAnalysis(APIView):

    @method_decorator(cache_page(60 * 60 * 2))
    @method_decorator(vary_on_cookie)
    def get(self, request, format=None):

        if 'query' in request.GET.keys() and 'email' in request.GET.keys() and 'password' in request.GET.keys():

            user_set = get_user_details(request.GET['email'], request.GET['password'])

            if len(user_set) > 0:
                if user_set[0].email_verified:
                    if user_set[0].quick_analysis_counter < user_set[0].plan_subscribed.quick_analysis_quota:
                        tweet = helpers.TwitterHelper(request.GET['query'])
                        data = tweet.fetch_analysis()

                        success = UserModel.objects.filter(id=user_set[0].id).update(
                            quick_analysis_counter=user_set[0].quick_analysis_counter + 1
                        )

                        if success == 1:
                            response = utils.BuildResponse(data)
                        else:
                            response = {
                                'status': status.HTTP_404_NOT_FOUND,
                                'message': 'Something went wrong, Code: CNSU1'
                            }
                    else:
                        response = {
                            'status': status.HTTP_400_BAD_REQUEST,
                            'message': 'You have exhausted your quick analysis quota'
                        }
                else:
                    response = {
                        'status': status.HTTP_400_BAD_REQUEST,
                        'message': 'Email is not verified'
                    }
            else:
                response = {
                    'status': status.HTTP_401_UNAUTHORIZED,
                    'message': 'Email does not exist or password is incorrect'
                }
        else:
            response = {
                'status': status.HTTP_400_BAD_REQUEST,
                'message': 'Invalid or missing Parameters'
            }

        return Response(response)
