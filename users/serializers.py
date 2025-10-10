from rest_framework import serializers
from .models import User, AuthCode
from django.core.validators import RegexValidator


class UserSerializer(serializers.ModelSerializer):
    referrals = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('id', 'phone', 'invite_code', 'activated_invite_code', 'referrals')
        read_only_fields = ('id', 'invite_code', 'referrals')

    def get_referrals(self, obj):
        """Получить список рефералов"""
        referrals = obj.get_referrals()
        return [referral.phone for referral in referrals]


class PhoneAuthSerializer(serializers.Serializer):
    phone = serializers.CharField(
        max_length=17,
        validators=[
            RegexValidator(
                regex=r'^\+?1?\d{9,15}$',
                message="Phone number must be entered in the format: '+79123456789'"
            )
        ]
    )


class VerifyCodeSerializer(serializers.Serializer):
    phone = serializers.CharField(max_length=17)
    code = serializers.CharField(max_length=4)


class ActivateInviteCodeSerializer(serializers.Serializer):
    invite_code = serializers.CharField(max_length=6)


class ProfileSerializer(serializers.ModelSerializer):
    referrals = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('phone', 'invite_code', 'activated_invite_code', 'referrals')
        read_only_fields = ('phone', 'invite_code', 'referrals')

    def get_referrals(self, obj):
        referrals = obj.get_referrals()
        return [referral.phone for referral in referrals]