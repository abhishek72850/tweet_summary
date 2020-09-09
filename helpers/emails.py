from django.core.mail import send_mail
from django.template.loader import get_template
from django.utils.html import strip_tags

from datetime import datetime, timedelta

from helpers.auths import generate_token
from tweet_summary.settings import SECRET_KEY, SITE_EMAIL, SENDGRID_API_KEY

from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail


def send_email(data):
    message = Mail(
        from_email=SITE_EMAIL,
        to_emails=data['email'],
        subject=data['subject'],
        html_content=data['html_text'])
    try:
        sg = SendGridAPIClient(SENDGRID_API_KEY)
        response = sg.send(message)
        print(response.status_code)
    except Exception as e:
        print(e.message)
        return False
    return True


def send_email_verification_link(user, email_verification_url):
    data = dict()
    data["confirmation_url"] = email_verification_url
    data["subject"] = "Please Confirm The Email"
    data["email"] = user.email
    template = get_template("app_ui/email_templates/email_verify.html")
    data["html_text"] = template.render(data)
    data["plain_text"] = strip_tags(data["html_text"])
    return send_email(data)


def send_subscription_verification_link(subscriber, subscription_confirmation_url):
    data = dict()
    data["confirmation_url"] = subscription_confirmation_url
    data["subject"] = "Please Confirm The Subscription"
    data["email"] = subscriber.user.email
    data["topic"] = subscriber.topic
    data["start_date"] = subscriber.subscription_from
    data["end_date"] = subscriber.subscription_to
    template = get_template("app_ui/email_templates/subscription_verify.html")
    data["html_text"] = template.render(data)
    data["plain_text"] = strip_tags(data["html_text"])
    return send_email(data)


def send_plan_change_confirmation(plan_request):
    data = dict()
    data["subject"] = "Plan Changed Confirmation"
    data["email"] = plan_request.user.email
    if plan_request.old_plan is None:
        data["old_plan"] = '-'
    else:
        data["old_plan"] = plan_request.old_plan.plan_name
    data["new_plan"] = plan_request.new_plan.plan_name
    template = get_template("app_ui/email_templates/plan_changed.html")
    data["html_text"] = template.render(data)
    data["plain_text"] = strip_tags(data["html_text"])
    return send_email(data)


def send_password_reset_link(user, password_reset_url):
    data = dict()
    data["confirmation_url"] = password_reset_url
    data["subject"] = "Password Reset"
    data["email"] = user.email
    template = get_template("app_ui/email_templates/password_reset.html")
    data["html_text"] = template.render(data)
    data["plain_text"] = strip_tags(data["html_text"])
    return send_email(data)


def send_plan_renew_confirmation(user):
    data = dict()
    data["subject"] = "Plan Renewal Confirmation"
    data["email"] = user.email
    data["plan_name"] = user.plan_subscribed.plan_name
    template = get_template("app_ui/email_templates/plan_renewed.html")
    data["html_text"] = template.render(data)
    data["plain_text"] = strip_tags(data["html_text"])
    return send_email(data)


def send_analysis(subscriber, analysis):
    current_date = datetime.now()
    token = generate_token(subscriber.user.email, expire=1, subscription_id=subscriber.id)
    analysis['unsubscribe_link'] = 'https://tweet-summary.herokuapp.com/subscriber/unsubscribe?verification_code={}'.format(token)
    template = get_template("subscriber/tweet_analysis.html")

    mail_data = {
        'subject': '{} Tweet analysis on {}'.format(current_date.date(), subscriber.topic),
        'email': subscriber.user.email,
        'html_text': template.render(analysis),
    }

    mail_data['plain_text'] = strip_tags(mail_data['html_text'])

    return send_email(mail_data)

