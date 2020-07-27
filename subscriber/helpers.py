import random
import string
import traceback
from datetime import datetime, timedelta

import jwt
from django.core.mail import send_mail
from django.template.loader import get_template
from django.utils.html import strip_tags

from api_manager.helpers import TwitterHelper
from api_manager.watson import Watson
from subscriber.models import SubscribeModel, UserModel, SubscriptionPlanModel
from tweet_summary.settings import SECRET_KEY, SITE_EMAIL


watson = Watson()


def random_string(string_length=20):
    """Generate a random string of fixed length """
    letters = string.ascii_letters + string.digits
    return ''.join(random.choice(letters) for i in range(string_length))


def generate_token(email, expire=7, **kwargs):
    exp_datetime = datetime.now() + timedelta(days=expire)

    payload = {
        'email': email,
        'exp': int(exp_datetime.strftime('%s'))
    }

    payload.update(kwargs)

    return jwt.encode(payload=payload, key=SECRET_KEY).decode('utf-8')


def decode_token(token):
    try:
        return True, jwt.decode(token, key=SECRET_KEY)
    except jwt.ExpiredSignatureError as e:
        print(traceback.format_exc())
        return False, None
    except jwt.DecodeError as e:
        print(traceback.format_exc())
        return False, None


def get_user_details(email, password):
    return UserModel.objects.filter(email=email, password=password)


def register_or_verify_subscriber(email, password, plan_id):
    result = get_user_details(email, password)

    print('*********', len(result))

    if len(result) == 0:
        user = UserModel()
        user.email = email
        user.password = password
        try:
            user.plan_subscribed = SubscriptionPlanModel.objects.get(id=plan_id)
        except SubscriptionPlanModel.DoesNotExist as err:
            return None

        user.save()

        return user

    return result[0]


def add_subscription(user, topic, start_date, end_date):
    if user.email_verified:
        result_set = SubscribeModel.objects.filter(user=user, topic=topic)

        quota = user.plan_subscribed.topic_quota
        count = SubscribeModel.objects.filter(user=user, subscription_status='ACTIVE').count()

        if count >= quota:
            return None, 'QUOTA_EXHAUSTED'

        if len(result_set) > 0:
            success = SubscribeModel.objects.filter(user=user, topic=topic).update(
                subscription_from=start_date,
                subscription_to=end_date
            )

            if success == 1:
                return result_set[0], 'UPDATED'
            else:
                return None, 'ERROR'
        else:
            subscriber = SubscribeModel()
            subscriber.user = user
            subscriber.topic = topic
            subscriber.subscription_from = start_date
            subscriber.subscription_to = end_date

            subscriber.save()

            return subscriber, 'CREATED'

    return None, 'NOT_VERIFIED'


def get_subscription_and_profile_details(email, password):
    full_details = {}
    user_set = get_user_details(email, password)
    print(user_set)
    if len(user_set) > 0:
        subscriptions = SubscribeModel.objects.filter(user=user_set[0])
        full_details = {
            'user': user_set[0].toJSON(),
            'plan': user_set[0].plan_subscribed.toJSON(),
            'subscriptions': [subscription.toJSON() for subscription in subscriptions]
        }

    return full_details


def remove_subscription(email, password, subscription_id):
    user_set = get_user_details(email, password)

    if len(user_set) > 0:
        SubscribeModel.objects.filter(user=user_set[0], id=subscription_id).delete()
    else:
        return False

    return True


def update_subscription_details(email, password, subscription_id, topic, subscription_from, subscription_to):
    user_set = get_user_details(email, password)

    if len(user_set) > 0:
        success = SubscribeModel.objects.filter(user=user_set[0], id=subscription_id).update(
            topic=topic,
            subscription_from=subscription_from,
            subscription_to=subscription_to
        )

        if success == 1:
            return True
        else:
            return False

    return False


def confirm_email_verification(email, user_id):
    result_set = UserModel.objects.filter(email=email, id=user_id)

    if len(result_set) > 0:
        success = UserModel.objects.filter(email=email, id=user_id).update(
            email_verified=True,
            status='VERIFIED',
            # subscription_status='ACTIVE'
        )

        if success == 1:
            return True

    return False


def confirm_subscription(email, subscription_id):
    result_set = SubscribeModel.objects.filter(id=subscription_id)

    if len(result_set) > 0:
        success = SubscribeModel.objects.filter(id=subscription_id).update(
            subscription_status='ACTIVE'
        )

        if success == 1:
            return True

    return False


def unsubscribe(email, subscription_id):
    result_set = SubscribeModel.objects.filter(id=subscription_id)

    if len(result_set) > 0:
        success = SubscribeModel.objects.filter(id=subscription_id).update(
            subscription_status='SUSPENDED'
        )

        if success == 1:
            return True

    return False


def send_sub_email(data):
    result = send_mail(data['subject'], data['plain_text'], SITE_EMAIL,
                       [data['email']], html_message=data['html_text'])
    return True


def send_email_verification_link(subscriber, email_verification_url):
    data = dict()
    data["confirmation_url"] = email_verification_url
    data["subject"] = "Please Confirm The Email"
    data["email"] = subscriber.email
    template = get_template("subscriber/email_verify.html")
    data["html_text"] = template.render(data)
    data["plain_text"] = strip_tags(data["html_text"])
    return send_sub_email(data)


def send_subscription_verification_link(subscriber, subscription_confirmation_url):
    data = dict()
    data["confirmation_url"] = subscription_confirmation_url
    data["subject"] = "Please Confirm The Subscription"
    data["email"] = subscriber.user.email
    data["topic"] = subscriber.topic
    data["start_date"] = subscriber.subscription_from
    data["end_date"] = subscriber.subscription_to
    template = get_template("subscriber/subscription_verify.html")
    data["html_text"] = template.render(data)
    data["plain_text"] = strip_tags(data["html_text"])
    return send_sub_email(data)


def prepare_twitter_analysis(topic):
    tweet = TwitterHelper(topic)
    data = tweet.fetch_analysis()

    positive_tweet = 0
    neutral_tweet = 0
    negative_tweet = 0

    todays_tweets = tweet.stats_for_24_hour()['tweet_list']

    for tweet_obj in todays_tweets:
        keywords = watson.extractKeywords(tweet_obj['text'])
        sentiment = watson.extractSentiment(tweet_obj['text'], keywords['data'])

        if sentiment['sentiment']['document']['label'] == 'positive':
            positive_tweet += 1
        elif sentiment['sentiment']['document']['label'] == 'negative':
            negative_tweet += 1
        elif sentiment['sentiment']['document']['label'] == 'neutral':
            neutral_tweet += 1

    if data['success']:
        print('Preparing....')
        data = data['data']
        analysis_data = {
            'query': data['query'],
            'increase': data['increase_in_tweets'],
            'total_tweets': data['total_tweets'],
            'total_mentions': len(data['total_mentions']),
            'total_retweets': data['total_retweets'],
            'total_favorite': data['total_favorite'],
            'total_todays_tweet': len(todays_tweets),
            'total_positive_tweets': positive_tweet,
            'total_negative_tweets': negative_tweet,
            'total_neutral_tweets': neutral_tweet
        }

        if data['increase_in_tweets'] < 0:
            analysis_data['increase_or_decrease'] = '{} decrease'.format(str(data['increase_in_tweets']*(-1)))
        else:
            analysis_data['increase_or_decrease'] = '{} increase'.format(str(data['increase_in_tweets']))

        mention_list = set()
        for value in data['noticeable_user']:
            mention_list.add(value[0])

        mention_list = list(mention_list)
        analysis_data['noticeable_user'] = ', '.join(mention_list[0:5])

        analysis_data['most_active_verified_tweet_user_name'] = data['most_active_verified_tweet']['user']['name']
        analysis_data['most_active_verified_tweet_retweets'] = data['most_active_verified_tweet']['retweet_count']
        analysis_data['most_active_verified_tweet_favorite'] = data['most_active_verified_tweet']['favorite_count']
        analysis_data['most_active_verified_tweet'] = data['most_active_verified_tweet']['text']

        mention_list = set()

        for value in data['most_active_verified_tweet']['entities']['user_mentions']:
            mention_list.add(value['name'])

        mention_list = list(mention_list)

        if len(mention_list) > 0:
            analysis_data['most_active_verified_tweet_mentions'] = ', '.join(mention_list)
        else:
            analysis_data['most_active_verified_tweet_mentions'] = 'None'

        analysis_data['noticeable_user_tweet_user_name_1'] = data['noticeable_user_tweet'][0]['user_name']
        analysis_data['noticeable_user_tweet_total_1'] = len(data['noticeable_user_tweet'][0]['tweet_content'])
        analysis_data['noticeable_user_tweet_total_retweets_1'] = data['noticeable_user_tweet'][0]['retweets_count']
        analysis_data['noticeable_user_tweet_total_favorite_1'] = data['noticeable_user_tweet'][0]['favorite_count']

        mention_list = set()

        for value in data['noticeable_user_tweet'][0]['mentions']:
            mention_list.add(value['name'])

        mention_list = list(mention_list)

        if len(mention_list) > 0:
            analysis_data['noticeable_user_tweet_mentions_1'] = ', '.join(mention_list)
        else:
            analysis_data['noticeable_user_tweet_mentions_1'] = 'None'

        analysis_data['noticeable_user_tweet_user_name_2'] = data['noticeable_user_tweet'][1]['user_name']
        analysis_data['noticeable_user_tweet_total_2'] = len(data['noticeable_user_tweet'][1]['tweet_content'])
        analysis_data['noticeable_user_tweet_total_retweets_2'] = data['noticeable_user_tweet'][1]['retweets_count']
        analysis_data['noticeable_user_tweet_total_favorite_2'] = data['noticeable_user_tweet'][1]['favorite_count']

        mention_list = set()

        for value in data['noticeable_user_tweet'][1]['mentions']:
            mention_list.add(value['name'])

        mention_list = list(mention_list)

        if len(mention_list) > 0:
            analysis_data['noticeable_user_tweet_mentions_2'] = ', '.join(mention_list)
        else:
            analysis_data['noticeable_user_tweet_mentions_2'] = 'None'

        return analysis_data
    else:
        return {'query': 'Something went wrong'}


def send_analysis(subscriber, analysis):
    current_date = datetime.now()
    token = generate_token(subscriber.user.email, expire=1, subscription_id=subscriber.id)
    analysis['unsubscribe_link'] = 'https://tweet-summary.herokuapp.com/subscriber/unsubscribe?verification_code={}'.format(token)
    template = get_template("subscriber/tweet_analysis.html")

    mail_data = {
        'subject' : '{} Tweet analysis on {}'.format(current_date.date(), subscriber.topic),
        'email' : subscriber.user.email,
        'html_text': template.render(analysis),
    }

    mail_data['plain_text'] = strip_tags(mail_data['html_text'])

    return send_sub_email(mail_data)
