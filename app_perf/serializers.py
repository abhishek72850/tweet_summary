from rest_framework import serializers

from app_perf.models import User, Subscribers


class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        max_length=128,
        min_length=8,
        write_only=True
    )

    class Meta:
        model = User
        fields = '__all__'


class SubscribersSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        max_length=128,
        min_length=8,
        write_only=True
    )

    class Meta:
        model = Subscribers
        fields = ['id', 'email', 'password', 'email_verified', 'status', 'plan_subscribed_at', 'plan_status', 'quick_analysis_counter']


