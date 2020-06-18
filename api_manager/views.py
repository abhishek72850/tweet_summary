from django.http import Http404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from . import utils, helpers

from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django.views.decorators.vary import vary_on_cookie

from django.shortcuts import render

# Create your views here.


class SummaryAnalysis(APIView):

    @method_decorator(cache_page(60*60*2))
    @method_decorator(vary_on_cookie)
    def get(self, request, format=None):

        if 'query' in request.GET.keys():
            tweet = helpers.TwitterHelper(request.GET['query'])
            data = tweet.fetch_analysis()

            response = utils.BuildResponse(data)

        else:
            response = {
                'status': status.HTTP_400_BAD_REQUEST,
                'message': 'Invalid or missing Parameters'
            }

        return Response(response)
