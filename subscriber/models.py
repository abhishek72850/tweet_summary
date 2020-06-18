from django.db import models

# Create your models here.


class SubscribeModel(models.Model):
    id = models.AutoField(primary_key=True, null=False, blank=True)
    email = models.EmailField(null=False, blank=True, max_length=200)
    status = models.CharField(max_length=64, null=False, blank=True, default='PENDING_VERIFICATION')
    topic = models.TextField(null=False, blank=False)
    created_at = models.DateTimeField(null=False, blank=True, auto_now_add=True)
    subscription_from = models.DateTimeField(null=False, blank=True)
    subscription_to = models.DateTimeField(null=False, blank=True)
    subscription_status = models.CharField(max_length=64, null=False, blank=True, default='IDLE')
    email_verified = models.BooleanField(default=False)

    class Meta:
        app_label = "subscriber"
        db_table = "tweet_subscribers"

    def __str__(self):
        return self.email
