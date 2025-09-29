from django.contrib.auth.models import AbstractUser
from django.db import models
import random
import string
from django.core.validators import RegexValidator


class User(AbstractUser):
    phone_regex = RegexValidator(
        regex=r'^\+?1?\d{9,15}$',
        message="Phone number must be entered in the format: '+79123456789'"
    )

    phone = models.CharField(
        validators=[phone_regex],
        max_length=17,
        unique=True,
        blank=True,
        null=True
    )
    invite_code = models.CharField(max_length=6, blank=True, null=True)
    activated_invite_code = models.CharField(max_length=6, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        # Генерируем инвайт-код при создании пользователя
        if not self.invite_code:
            self.generate_invite_code()
        super().save(*args, **kwargs)

    def generate_invite_code(self):
        """Генерация 6-значного инвайт-кода"""
        characters = string.ascii_uppercase + string.digits
        while True:
            code = ''.join(random.choices(characters, k=6))
            # Проверяем уникальность кода
            if not User.objects.filter(invite_code=code).exists():
                self.invite_code = code
                break

    def __str__(self):
        return self.phone if self.phone else self.username

    def activate_invite_code(self, code_to_activate):
        """Активация чужого инвайт-кода"""
        if not code_to_activate:
            return False, "Инвайт-код не может быть пустым"

        # Нельзя активировать свой же код
        if code_to_activate == self.invite_code:
            return False, "Нельзя активировать свой же инвайт-код"

        # Ищем пользователя с таким инвайт-кодом
        try:
            inviter = User.objects.get(invite_code=code_to_activate)
        except User.DoesNotExist:
            return False, "Инвайт-код не найден"

        # Проверяем не активировал ли уже код
        if self.activated_invite_code:
            return False, "Вы уже активировали инвайт-код"

        # Активируем код
        self.activated_invite_code = code_to_activate
        self.save()
        return True, "Инвайт-код успешно активирован"

    def get_referrals(self):
        """Получить список рефералов (кто ввел код этого пользователя)"""
        return User.objects.filter(activated_invite_code=self.invite_code)


class AuthCode(models.Model):
    phone = models.CharField(max_length=15)
    code = models.CharField(max_length=4)
    created_at = models.DateTimeField(auto_now_add=True)
    is_used = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.phone}: {self.code}"

    class Meta:
        indexes = [
            models.Index(fields=['phone', 'created_at']),
        ]