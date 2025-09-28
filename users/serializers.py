from rest_framework import serializers
from .models import User
import random


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'phone', 'invite_code', 'activated_invite_code')

class PhoneAuthSerializer(serializers.Serializer):
    phone = serializers.CharField(max_length=15)

class VerifyCodeSerializer(serializers.Serializer):
    phone = serializers.CharField(max_length=15)
    code = serializers.CharField(max_length=4)