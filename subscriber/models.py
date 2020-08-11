import copy
from django.db import models
from django.core import serializers
# Create your models here.


class GeneralObject:
    def toJSON(self):
        return serializers.serialize('json', [self])


class SubscriptionPlanModel(models.Model, GeneralObject):
    id = models.AutoField(primary_key=True, null=False, blank=True)
    plan_name = models.CharField(max_length=100, null=False)
    topic_quota = models.IntegerField(null=False)
    subscription_period_max_days = models.IntegerField(null=False)
    quick_analysis_quota = models.IntegerField(null=False)
    created_at = models.DateTimeField(null=False, blank=True, auto_now_add=True)

    class Meta:
        app_label = "subscriber"
        db_table = "tweet_subscription_plans"


class UserModel(models.Model, GeneralObject):
    id = models.AutoField(primary_key=True, null=False, blank=True)
    email = models.EmailField(null=False, blank=True, max_length=200, unique=True)
    password = models.CharField(max_length=64, null=False)
    created_at = models.DateTimeField(null=False, blank=True, auto_now_add=True)
    email_verified = models.BooleanField(default=False)
    status = models.CharField(max_length=64, null=False, blank=True, default='PENDING_VERIFICATION')
    plan_subscribed = models.ForeignKey(SubscriptionPlanModel, on_delete=models.DO_NOTHING)
    quick_analysis_counter = models.IntegerField(null=False, default=0)

    class Meta:
        app_label = "subscriber"
        db_table = "tweet_subscribers"


class SubscribeModel(models.Model, GeneralObject):
    id = models.AutoField(primary_key=True, null=False, blank=True)
    user = models.ForeignKey(UserModel, on_delete=models.DO_NOTHING)
    topic = models.TextField(null=False, blank=False)
    created_at = models.DateTimeField(null=False, blank=True, auto_now_add=True)
    subscription_from = models.DateTimeField(null=False, blank=True)
    subscription_to = models.DateTimeField(null=False, blank=True)
    subscription_status = models.CharField(max_length=64, null=False, blank=True, default='IDLE')

    class Meta:
        app_label = "subscriber"
        db_table = "tweet_subscriptions"

    def __str__(self):
        return self.topic


class PlanChangeRequestModel(models.Model, GeneralObject):
    id = models.AutoField(primary_key=True, null=False, blank=True)
    user = models.ForeignKey(UserModel, on_delete=models.DO_NOTHING)
    created_at = models.DateTimeField(null=False, blank=True, auto_now_add=True)
    old_plan = models.ForeignKey(SubscriptionPlanModel, on_delete=models.DO_NOTHING, related_name='old_plan')
    new_plan = models.ForeignKey(SubscriptionPlanModel, on_delete=models.DO_NOTHING, related_name='new_plan')
    status = models.CharField(max_length=64, null=False, blank=True, default='REQUESTED')

    class Meta:
        app_label = "subscriber"
        db_table = "tweet_plan_change_request"
