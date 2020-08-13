from datetime import datetime

from celery import shared_task
from subscriber.models import SubscribeModel
from subscriber.helpers import unsubscribe, prepare_twitter_analysis, send_analysis

import pytz

import requests


@shared_task
def ready():
    requests.get(url="https://tweet-summary.herokuapp.com/app/portal")
    print('Ready...')


@shared_task
def daily_service():
    utc = pytz.UTC
    result_set = SubscribeModel.objects.all()
    current_date = datetime.now(tz=utc)

    for subscription in result_set:
        print(subscription.user.email, subscription.topic)
        if (subscription.subscription_status == 'ACTIVE') and (
                subscription.subscription_from <= current_date <= subscription.subscription_to):
            analysis_data = prepare_twitter_analysis(subscription.topic)
            send_analysis(subscription, analysis_data)
        elif subscription.subscription_to < current_date and subscription.subscription_status != 'SUSPENDED':
            unsubscribe(subscription.user.email, subscription.id)
