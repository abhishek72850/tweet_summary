from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.contrib.auth.models import PermissionsMixin
from django.core.serializers.json import DjangoJSONEncoder
from django.utils.translation import ugettext_lazy as _

import json


class UserManager(BaseUserManager):

    def get_by_natural_key(self, email):
        return self.get(email=email)


class AdminsManager(BaseUserManager):

    def create_admin(self, email, password, **kwargs):
        if email is None:
            raise TypeError('Users must have an email address.')
        admin = self.model(
            email=self.normalize_email(email),
            **kwargs
        )
        admin.set_password(password)
        admin.save()
        return admin

    def create_superuser(self, email, password, **kwargs):
        """
        Create and save a SuperUser with the given email and password.
        """
        kwargs.setdefault('is_staff', True)
        kwargs.setdefault('is_superuser', True)
        kwargs.setdefault('is_active', True)

        if kwargs.get('is_staff') is not True:
            raise ValueError(_('Superuser must have is_staff=True.'))
        if kwargs.get('is_superuser') is not True:
            raise ValueError(_('Superuser must have is_superuser=True.'))

        return self.create_admin(email=email, password=password, **kwargs)


class SubscribersManager(BaseUserManager):

    def create_subscriber(self, email, password=None, **kwargs):
        if email is None:
            raise TypeError('Users must have an email address.')
        employee = Subscribers(email=self.normalize_email(email), **kwargs)
        employee.set_password(password)
        employee.save()
        return employee


class GeneralObject:

    def toJSON(self):
        return json.dumps(self.__dict__, sort_keys=True, default=str)


class SubscriberPlanModel(models.Model, GeneralObject):
    id = models.AutoField(primary_key=True, null=False, blank=True)
    plan_name = models.CharField(max_length=100, null=False)
    plan_duration = models.IntegerField(null=False)
    topic_quota = models.IntegerField(null=False)
    subscription_period_max_days = models.IntegerField(null=False)
    quick_analysis_quota = models.IntegerField(null=False)
    created_at = models.DateTimeField(null=False, blank=True, auto_now_add=True)

    class Meta:
        app_label = "app_perf"
        db_table = "subscriber_plan"


class User(AbstractBaseUser, PermissionsMixin, GeneralObject):
    email = models.EmailField(db_index=True, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    USERNAME_FIELD = 'email'

    objects = UserManager()

    def __str__(self):
        return self.email


class Admins(User, PermissionsMixin):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = AdminsManager()


class Subscribers(User, PermissionsMixin):
    email_verified = models.BooleanField(default=False)
    status = models.CharField(max_length=64, null=False, blank=True, default='PENDING_VERIFICATION')
    plan_subscribed_at = models.DateTimeField(null=True, blank=True)
    plan_subscribed = models.ForeignKey(SubscriberPlanModel, on_delete=models.DO_NOTHING, null=True)
    plan_status = models.CharField(max_length=64, null=False, blank=True, default='NOT_ASSIGNED')
    quick_analysis_counter = models.IntegerField(null=False, default=0)
    timezone_offset = models.IntegerField(null=False, default=0)

    # Django auth columns
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = SubscribersManager()

    # def toJSON(self):
    #     print('*****', self.__dict__)
    #     print('#####', User.__dict__)
    #     return serializers.serialize('json', [self, User.objects.get(id=self.id)], fields=('email_verified','email'))


class SubscriptionModel(models.Model, GeneralObject):
    id = models.AutoField(primary_key=True, null=False, blank=True)
    user = models.ForeignKey(Subscribers, on_delete=models.DO_NOTHING)
    topic = models.TextField(null=False, blank=False)
    created_at = models.DateTimeField(null=False, blank=True, auto_now_add=True)
    subscription_from = models.DateTimeField(null=False, blank=True)
    subscription_to = models.DateTimeField(null=False, blank=True)
    subscription_status = models.CharField(max_length=64, null=False, blank=True, default='IDLE')

    class Meta:
        app_label = "app_perf"
        db_table = "subscription"

    def __str__(self):
        return self.topic


class PlanChangeRequestModel(models.Model, GeneralObject):
    id = models.AutoField(primary_key=True, null=False, blank=True)
    user = models.ForeignKey(Subscribers, on_delete=models.DO_NOTHING)
    created_at = models.DateTimeField(null=False, blank=True, auto_now_add=True)
    old_plan = models.ForeignKey(SubscriberPlanModel, on_delete=models.DO_NOTHING, null=True, related_name='old_plan')
    new_plan = models.ForeignKey(SubscriberPlanModel, on_delete=models.DO_NOTHING, null=False, related_name='new_plan')
    status = models.CharField(max_length=64, null=False, blank=True, default='REQUESTED')

    class Meta:
        app_label = "app_perf"
        db_table = "plan_change_request"


class UpcomingPlanModel(models.Model, GeneralObject):
    id = models.AutoField(primary_key=True, null=False, blank=True)
    user = models.ForeignKey(Subscribers, on_delete=models.DO_NOTHING)
    created_at = models.DateTimeField(null=False, blank=True, auto_now_add=True)
    plan = models.ForeignKey(SubscriberPlanModel, on_delete=models.DO_NOTHING, related_name='plan')
    plan_starts_from = models.DateTimeField(null=False, blank=True)
    status = models.CharField(max_length=64, null=False, blank=True, default='IN_QUEUE')

    class Meta:
        app_label = "app_perf"
        db_table = "upcoming_plan"


class UserPlanHistoryModel(models.Model, GeneralObject):
    id = models.AutoField(primary_key=True, null=False, blank=True)
    user = models.ForeignKey(Subscribers, on_delete=models.DO_NOTHING)
    created_at = models.DateTimeField(null=False, blank=True, auto_now_add=True)
    plan = models.ForeignKey(SubscriberPlanModel, on_delete=models.DO_NOTHING, related_name='plan_history')
    plan_started_from = models.DateTimeField(null=False, blank=True)
    payment_id = models.CharField(max_length=200, null=True, blank=True)
    payment_mode = models.CharField(max_length=64, null=True, blank=True)

    class Meta:
        app_label = "app_perf"
        db_table = "user_plan_history"


