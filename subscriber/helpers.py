import random
import string
import traceback
from datetime import datetime, timedelta

import jwt
from django.core.mail import send_mail
from django.template.loader import get_template
from django.utils.html import strip_tags

from api_manager.helpers import TwitterHelper
from subscriber.models import SubscribeModel
from tweet_summary.settings import SECRET_KEY, SITE_EMAIL


def random_string(string_length=20):
    """Generate a random string of fixed length """
    letters = string.ascii_letters + string.digits
    return ''.join(random.choice(letters) for i in range(string_length))


def generate_token(email, subscriber_id, expire=7):
    exp_datetime = datetime.now() + timedelta(days=expire)

    payload = {
        'subscriber_id': subscriber_id,
        'email': email,
        'exp': int(exp_datetime.strftime('%s'))
    }

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


def add_subscriber(email, topic, start_date, end_date):
    result_set = SubscribeModel.objects.filter(email=email, topic=topic)

    if len(result_set) > 0:
        success = SubscribeModel.objects.filter(email=email, topic=topic).update(
            subscription_from=start_date,
            subscription_to=end_date
        )

        if success == 1:
            return result_set[0], 'UPDATED'
        else:
            return None, 'ERROR'
    else:
        subscriber = SubscribeModel()
        subscriber.email = email
        subscriber.topic = topic
        subscriber.subscription_from = start_date
        subscriber.subscription_to = end_date

        subscriber.save()

        return subscriber, 'CREATED'


def confirm_email_verification(email, subscriber_id):
    result_set = SubscribeModel.objects.filter(email=email, id=subscriber_id)

    if len(result_set) > 0:
        success = SubscribeModel.objects.filter(email=email, id=subscriber_id).update(
            email_verified=True,
            status='VERIFIED',
            subscription_status='ACTIVE'
        )

        if success == 1:
            return True

    return False


def unsubscribe(email, subscriber_id):
    result_set = SubscribeModel.objects.filter(email=email, id=subscriber_id, email_verified=True, status='VERIFIED')

    if len(result_set) > 0:
        success = SubscribeModel.objects.filter(email=email, id=subscriber_id).update(
            subscription_status='SUSPENDED'
        )

        if success == 1:
            return True

    return False


def send_sub_email(data):
    result = send_mail(data['subject'], data['plain_text'], SITE_EMAIL,
                       [data['email']], html_message=data['html_text'])
    return True


def send_subscription_email(subscriber, subscription_confirmation_url):
    data = dict()
    data["confirmation_url"] = subscription_confirmation_url
    data["subject"] = "Please Confirm The Subscription"
    data["email"] = subscriber.email
    data["start_date"] = subscriber.subscription_from
    data["end_date"] = subscriber.subscription_to
    template = get_template("subscriber/email_verify.html")
    data["html_text"] = template.render(data)
    data["plain_text"] = strip_tags(data["html_text"])
    return send_sub_email(data)


def prepare_twitter_analysis(topic):
    tweet = TwitterHelper(topic)
    data = tweet.fetch_analysis()

    if data['success']:
        print('Preparing....')
        data = data['data']
        analysis_data = {
            'query': data['query'],
            'increase': data['increase_in_tweets'],
            'total_tweets': data['total_tweets'],
            'total_mentions': len(data['total_mentions']),
            'total_retweets': data['total_retweets'],
            'total_favorite': data['total_favorite']
        }

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
    token = generate_token(subscriber.email, subscriber.id, expire=1)
    analysis['unsubscribe_link'] = 'https://tweet-summary.herokuapp.com/subscriber/unsubscribe?verification_code={}'.format(token)
    template = get_template("subscriber/tweet_analysis.html")

    mail_data = {
        'subject' : '{} Tweet analysis on {}'.format(current_date.date(), subscriber.topic),
        'email' : subscriber.email,
        'html_text': template.render(analysis),
    }

    mail_data['plain_text'] = strip_tags(mail_data['html_text'])

    return send_sub_email(mail_data)
