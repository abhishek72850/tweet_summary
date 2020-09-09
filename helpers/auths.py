import random
import string
import traceback
from datetime import datetime, timedelta

import jwt

from tweet_summary.settings import SECRET_KEY


def generate_token(email, expire=7, **kwargs):
    exp_datetime = datetime.utcnow() + timedelta(days=expire)
    payload = {
        'email': email,
        'exp': exp_datetime
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


def is_action_allowed(user):
    if not user.email_verified:
        return 'Email not verified'

    if user.plan_status != 'ACTIVE':
        return 'Plan not assigned or expired'

    if user.status == 'SUSPENDED':
        return 'User Suspended'

    return True


