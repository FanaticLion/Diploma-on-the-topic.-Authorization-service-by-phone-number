from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView
from rest_framework import serializers
from .models import User


class UserProfileSerializer(serializers.ModelSerializer):
    referrals = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['phone', 'invite_code', 'activated_invite_code', 'referrals']

    def get_referrals(self, obj):
        """Получить список телефонов рефералов"""
        referrals = obj.get_referrals()
        return [user.phone for user in referrals]