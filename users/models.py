from django.contrib.auth.models import AbstractUser
from django.db import models
import random
import string
from django.core.validators import RegexValidator
from django.contrib.auth.models import BaseUserManager
from django.utils import timezone


class UserManager(BaseUserManager):
    def create_user(self, phone, password=None, **extra_fields):
        if not phone:
            raise ValueError('Phone number is required')

        # Автоматически создаем username если не предоставлен
        if not extra_fields.get('username'):
            extra_fields['username'] = f"user_{phone}"

        user = self.model(phone=phone, **extra_fields)
        if password:
            user.set_password(password)
        else:
            user.set_unusable_password()
        user.save(using=self._db)
        return user

    def create_superuser(self, phone, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        if not extra_fields.get('username'):
            extra_fields['username'] = f"admin_{phone}"

        return self.create_user(phone, password, **extra_fields)


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

    objects = UserManager()

    USERNAME_FIELD = 'phone'
    REQUIRED_FIELDS = []

    def save(self, *args, **kwargs):
        # Генерируем инвайт-код при создании пользователя
        if not self.invite_code:
            self.invite_code = self.generate_invite_code()
        super().save(*args, **kwargs)

    def generate_invite_code(self):
        """Генерация 6-значного инвайт-кода"""
        characters = string.ascii_uppercase + string.digits
        while True:
            code = ''.join(random.choices(characters, k=6))
            # Проверяем уникальность кода
            if not User.objects.filter(invite_code=code).exists():
                return code

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

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'


class AuthCode(models.Model):
    phone = models.CharField(max_length=15)
    code = models.CharField(max_length=4)
    created_at = models.DateTimeField(auto_now_add=True)
    is_used = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.phone}: {self.code}"

    def is_valid(self):
        """Проверяет валидность кода (5 минут)"""
        return (timezone.now() - self.created_at).total_seconds() < 300 and not self.is_used

    class Meta:
        indexes = [
            models.Index(fields=['phone', 'created_at']),
        ]
        verbose_name = 'Код авторизации'
        verbose_name_plural = 'Коды авторизации'