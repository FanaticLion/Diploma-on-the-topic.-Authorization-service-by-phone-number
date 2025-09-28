# users/models.py
from django.contrib.auth.models import AbstractUser
from django.db import models
import random
import string


class User(AbstractUser):
    phone = models.CharField(max_length=15, unique=True, blank=True, null=True)
    invite_code = models.CharField(max_length=6, unique=True, blank=True)
    activated_invite_code = models.CharField(max_length=6, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def generate_invite_code(self):
        """Генерация 6-значного инвайт-кода"""
        characters = string.ascii_uppercase + string.digits
        code = ''.join(random.choices(characters, k=6))
        self.invite_code = code
        self.save()

    def __str__(self):
        return self.phone if self.phone else self.username


class AuthCode(models.Model):
    phone = models.CharField(max_length=15)
    code = models.CharField(max_length=4)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.phone}: {self.code}"