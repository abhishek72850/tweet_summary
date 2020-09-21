import random
import string
import json
import traceback
import pytz
from datetime import datetime, timedelta

from app_perf.models import Subscribers, SubscriptionModel, SubscriberPlanModel, PlanChangeRequestModel, UpcomingPlanModel, UserPlanHistoryModel
from app_perf.serializers import SubscribersSerializer


def get_user_by_id(user_id):
    return Subscribers.objects.filter(id=user_id)


def get_user_by_email(email):
    return Subscribers.objects.filter(email=email)


def get_all_users():
    return Subscribers.objects.all()


def get_subscription_by_id(subscription_id):
    return SubscriptionModel.objects.filter(id=subscription_id)


def get_all_subscriptions():
    return SubscriptionModel.objects.all().order_by('-created_at')


def get_user_details(email, password):
    return Subscribers.objects.filter(email=email, password=password)


def get_plan_request_by_id(request_id):
    return PlanChangeRequestModel.objects.filter(id=request_id)


def get_all_plan_change_requests():
    return PlanChangeRequestModel.objects.all().order_by('-created_at')


def get_all_upcoming_user_plans():
    return UpcomingPlanModel.objects.all().order_by('-created_at')


def get_all_user_plan_history():
    return UserPlanHistoryModel.objects.all().order_by('-created_at')


def get_plan_by_id(plan_id):
    return SubscriberPlanModel.objects.filter(id=plan_id)


def delete_all_user_subscriptions(user):
    return SubscriberPlanModel.objects.filter(user=user).delete()


def is_user_plan_expired(user):
    if (user.plan_subscribed_at + timedelta(days=user.plan_subscribed.plan_duration)) < datetime.now(tz=pytz.UTC):
        return True
    return False


def get_account_details(user_id):
    full_details = {}
    user_set = get_user_by_id(user_id)

    if len(user_set) > 0:
        subscriptions = SubscriptionModel.objects.filter(user=user_set[0])

        full_details = {
            'user': user_set[0].toJSON(),
            'plan': user_set[0].plan_subscribed.toJSON() if user_set[0].plan_subscribed is not None else None,
            'subscriptions': [subscription.toJSON() for subscription in subscriptions]
        }

    return full_details


def update_user_password(user_id, password):
    success = Subscribers.objects.filter(id=user_id).update(
        password=password
    )

    return success


def update_user_status(user_id, status):
    success = Subscribers.objects.filter(id=user_id).update(
        status=status
    )

    return success


def update_subscription_status(subscription_id, status):
    success = SubscriptionModel.objects.filter(id=subscription_id).update(
        subscription_status=status
    )

    return success


def update_plan_request_status(plan_id, status):
    success = PlanChangeRequestModel.objects.filter(id=plan_id).update(
        status=status
    )

    return success


def update_user_plan(user, plan, status='ACTIVE'):
    success = Subscribers.objects.filter(id=user.id).update(
        plan_status=status,
        plan_subscribed=plan,
        plan_subscribed_at=datetime.now(tz=pytz.UTC)
    )

    return success


def update_quick_analysis_counter(user):
    success = Subscribers.objects.filter(id=user.id).update(
        quick_analysis_counter=user.quick_analysis_counter + 1
    )

    return success


def remove_subscription(user, subscription_id):
    SubscriptionModel.objects.filter(user=user, id=subscription_id).delete()
    return True


def update_subscription_details(user, subscription_id, topic, subscription_from, subscription_to):
    success = SubscriptionModel.objects.filter(user=user, id=subscription_id).update(
        topic=topic,
        subscription_from=subscription_from,
        subscription_to=subscription_to
    )

    if success == 1:
        return True
    else:
        return False


def record_plan_history(user, plan, plan_started_from, payment_id='', payment_mode='OFFLINE'):
    history = UserPlanHistoryModel()
    history.user = user
    history.plan = plan
    history.plan_started_from = plan_started_from
    history.payment_id = payment_id
    history.payment_mode = payment_mode

    history.save()
    
    return history


def is_topic_quota_exhausted(user):
    quota = user.plan_subscribed.topic_quota
    count = SubscriptionModel.objects.filter(user=user, subscription_status='ACTIVE').count()

    return count >= quota


def add_subscription(user, topic, start_date, end_date):

    result_set = SubscriptionModel.objects.filter(user=user, topic=topic)

    if is_topic_quota_exhausted(user):
        return None, 'QUOTA_EXHAUSTED'

    if len(result_set) > 0:
        success = SubscriptionModel.objects.filter(user=user, topic=topic).update(
            subscription_from=start_date,
            subscription_to=end_date
        )

        if success == 1:
            return result_set[0], 'UPDATED'
        else:
            return None, 'ERROR'

    subscriber = SubscriptionModel()
    subscriber.user = user
    subscriber.topic = topic
    subscriber.subscription_from = start_date
    subscriber.subscription_to = end_date

    subscriber.save()

    return subscriber, 'CREATED'


def add_plan_request(user, plan):
    request_set = PlanChangeRequestModel.objects.filter(user=user, status='REQUESTED')

    for plan_request in request_set:
        PlanChangeRequestModel.objects.filter(id=plan_request.id).update(
            status='CANCELLED'
        )

    plan_request = PlanChangeRequestModel()
    plan_request.user = user
    plan_request.old_plan = user.plan_subscribed
    plan_request.new_plan = plan
    plan_request.save()
    return plan_request


def register_or_verify_subscriber(email, password, plan_id):
    result = get_user_details(email, password)

    if len(result) == 0:
        user = Subscribers()
        user.email = email
        user.password = password
        try:
            user.plan_subscribed = SubscriberPlanModel.objects.get(id=plan_id)
        except SubscriberPlanModel.DoesNotExist as err:
            return None

        user.save()

        return user

    return result[0]


def get_plan_starts_from(user):
    plan_starts_from = user.plan_subscribed_at
    plan_duration = user.plan_subscribed.plan_duration
    for upcoming in get_all_upcoming_user_plans():
        if user.id == upcoming.user.id and plan_starts_from < upcoming.plan_starts_from:
            plan_starts_from = upcoming.plan_starts_from
            plan_duration = upcoming.plan.plan_duration
    return plan_starts_from + timedelta(days=plan_duration)


def add_upcoming_plan(user, plan):
    upcoming = UpcomingPlanModel()
    upcoming.user = user
    upcoming.plan = plan
    upcoming.plan_starts_from = get_plan_starts_from(user)

    upcoming.save()

    return upcoming


def confirm_email_verification(email, user_id):
    result_set = Subscribers.objects.filter(email=email, id=user_id)

    if len(result_set) > 0:
        success = Subscribers.objects.filter(email=email, id=user_id).update(
            email_verified=True,
            status='VERIFIED',
        )

        if success == 1:
            return True

    return False


def confirm_subscription(email, subscription_id):
    result_set = SubscriptionModel.objects.filter(id=subscription_id)

    if len(result_set) > 0:
        success = SubscriptionModel.objects.filter(id=subscription_id).update(
            subscription_status='ACTIVE'
        )

        if success == 1:
            return True

    return False


def unsubscribe(email, subscription_id, status='UNSUBSCRIBED'):
    result_set = SubscriptionModel.objects.filter(id=subscription_id)

    if len(result_set) > 0:
        success = SubscriptionModel.objects.filter(id=subscription_id).update(
            subscription_status=status
        )

        if success == 1:
            return True

    return False


