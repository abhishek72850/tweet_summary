import pytz
from datetime import datetime, timedelta

from django.contrib.sites.shortcuts import get_current_site


def get_host_origin(request):
    protocol = 'http://'
    if 'HTTPS' in request.META['SERVER_PROTOCOL']:
        protocol = 'https://'
    return f'{protocol}{get_current_site(request).domain}'


def request_contain_keys(request_dict, keys):
    """
    Checks if given keys list present in the api request
    :param request_dict:dict
    :param keys:list
    :return:
    """
    for key in keys:
        if key not in request_dict.keys():
            return False
    return True


def get_utc_now():
    return datetime.now(tz=pytz.UTC)
