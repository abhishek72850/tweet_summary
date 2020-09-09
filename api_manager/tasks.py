from datetime import datetime, timedelta

from celery import shared_task
from app_perf.models import SubscriptionModel, UpcomingPlanModel, Subscribers

from helpers.db import unsubscribe, delete_all_user_subscriptions, get_all_users, get_all_subscriptions, get_all_upcoming_user_plans, update_user_plan
from helpers.emails import send_analysis
from helpers.analysis import prepare_twitter_analysis

import pytz

import requests


@shared_task
def ready():
    requests.get(url="https://tweet-summary.herokuapp.com/app")
    print('Ready...')


@shared_task
def daily_service():
    utc = pytz.UTC
    result_set = get_all_subscriptions()
    current_date = datetime.now(tz=utc)

    for subscription in result_set:
        print(subscription.user.email, subscription.topic)
        if (subscription.subscription_status == 'ACTIVE') and (
                subscription.subscription_from <= current_date <= subscription.subscription_to):
            analysis_data = prepare_twitter_analysis(subscription.topic)
            send_analysis(subscription, analysis_data)
        elif subscription.subscription_to < current_date and subscription.subscription_status not in ['SUSPENDED', 'UNSUBSCRIBED', 'EXPIRED']:
            unsubscribe(subscription.user.email, subscription.id, status='EXPIRED')


@shared_task
def plan_update_service():
    current_date = datetime.now(tz=pytz.UTC)
    upcoming_plan_set = get_all_upcoming_user_plans()

    for user in get_all_users():
        if user.plan_subscribed_at + timedelta(days=user.plan_subscribed.plan_duration) <= current_date:
            Subscribers.objects.filter(id=user.id).update(
                plan_status='EXPIRED'
            )
            SubscriptionModel.objects.filter(user=user).update(
                status='EXPIRED'
            )

    for upcoming in upcoming_plan_set:
        if upcoming.plan_starts_from.date() == current_date.date():
            SubscriptionModel.objects.filter(user=upcoming.user).update(
                status='EXPIRED'
            )
            # if upcoming.user.plan_subscribed.id > upcoming.plan.id:
            #     delete_all_user_subscriptions(upcoming.user)

            update_user_plan(upcoming.user, upcoming.plan)
