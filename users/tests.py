from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from .models import AuthCode
from .schema import UserProfileSerializer
import re

User = get_user_model()


class UserModelTests(TestCase):
    def test_create_user_with_phone(self):
        """Тест создания пользователя с номером телефона"""
        user = User.objects.create_user(
            phone='+79111111111',
            password='testpass123'
        )
        self.assertEqual(user.phone, '+79111111111')
        self.assertTrue(user.is_active)
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)

    def test_user_invite_code_generation(self):
        """Тест автоматической генерации инвайт-кода"""
        user = User.objects.create_user(phone='+79111111111')
        self.assertIsNotNone(user.invite_code)
        self.assertEqual(len(user.invite_code), 6)
        # Проверяем, что код состоит из букв и цифр
        self.assertTrue(re.match(r'^[A-Z0-9]{6}$', user.invite_code))

    def test_unique_invite_codes(self):
        """Тест уникальности инвайт-кодов"""
        user1 = User.objects.create_user(phone='+79111111111')
        user2 = User.objects.create_user(phone='+79222222222')
        self.assertNotEqual(user1.invite_code, user2.invite_code)

    def test_activate_invite_code(self):
        """Тест активации инвайт-кода"""
        user1 = User.objects.create_user(phone='+79111111111')
        user2 = User.objects.create_user(phone='+79222222222')

        # Активируем код первого пользователя у второго
        success, message = user2.activate_invite_code(user1.invite_code)

        self.assertTrue(success)
        self.assertEqual(user2.activated_invite_code, user1.invite_code)

    def test_activate_own_invite_code(self):
        """Тест невозможности активации собственного кода"""
        user = User.objects.create_user(phone='+79111111111')
        success, message = user.activate_invite_code(user.invite_code)

        self.assertFalse(success)
        self.assertIn('свой же инвайт-код', message)

    def test_activate_nonexistent_code(self):
        """Тест активации несуществующего кода"""
        user = User.objects.create_user(phone='+79111111111')
        success, message = user.activate_invite_code('INVALID')

        self.assertFalse(success)
        self.assertIn('не найден', message)

    def test_get_referrals(self):
        """Тест получения рефералов"""
        user1 = User.objects.create_user(phone='+79111111111')
        user2 = User.objects.create_user(phone='+79222222222')
        user3 = User.objects.create_user(phone='+79333333333')

        # Активируем код у двух пользователей
        user2.activate_invite_code(user1.invite_code)
        user3.activate_invite_code(user1.invite_code)

        referrals = user1.get_referrals()
        self.assertEqual(referrals.count(), 2)
        self.assertIn(user2, referrals)
        self.assertIn(user3, referrals)


class AuthCodeModelTests(TestCase):
    def test_create_auth_code(self):
        """Тест создания кода авторизации"""
        auth_code = AuthCode.objects.create(
            phone='+79111111111',
            code='1234'
        )
        self.assertEqual(auth_code.phone, '+79111111111')
        self.assertEqual(auth_code.code, '1234')
        self.assertFalse(auth_code.is_used)


class SchemaTests(TestCase):
    def setUp(self):
        """Настройка тестовых данных"""
        self.user = User.objects.create_user(phone='+79111111111')
        self.referral = User.objects.create_user(phone='+79222222222')
        self.referral.activate_invite_code(self.user.invite_code)

    def test_user_profile_serializer_fields(self):
        """Тест полей UserProfileSerializer"""
        serializer = UserProfileSerializer(instance=self.user)

        # Проверяем наличие всех полей
        expected_fields = ['phone', 'invite_code', 'activated_invite_code', 'referrals']
        for field in expected_fields:
            self.assertIn(field, serializer.data)

    def test_user_profile_serializer_phone(self):
        """Тест поля phone в сериализаторе"""
        serializer = UserProfileSerializer(instance=self.user)
        self.assertEqual(serializer.data['phone'], '+79111111111')

    def test_user_profile_serializer_invite_code(self):
        """Тест поля invite_code в сериализаторе"""
        serializer = UserProfileSerializer(instance=self.user)
        self.assertEqual(serializer.data['invite_code'], self.user.invite_code)
        self.assertEqual(len(serializer.data['invite_code']), 6)

    def test_user_profile_serializer_activated_invite_code(self):
        """Тест поля activated_invite_code в сериализаторе"""
        serializer = UserProfileSerializer(instance=self.user)
        self.assertEqual(serializer.data['activated_invite_code'], self.user.activated_invite_code)

    def test_user_profile_serializer_referrals(self):
        """Тест поля referrals в сериализаторе"""
        serializer = UserProfileSerializer(instance=self.user)

        # Проверяем, что referrals - это список
        self.assertIsInstance(serializer.data['referrals'], list)

        # Проверяем содержимое referrals
        self.assertIn('+79222222222', serializer.data['referrals'])
        self.assertEqual(len(serializer.data['referrals']), 1)

    def test_user_profile_serializer_empty_referrals(self):
        """Тест пустого списка referrals"""
        user_without_referrals = User.objects.create_user(phone='+79333333333')
        serializer = UserProfileSerializer(instance=user_without_referrals)

        self.assertEqual(serializer.data['referrals'], [])
        self.assertEqual(len(serializer.data['referrals']), 0)


class AuthAPITests(APITestCase):
    def setUp(self):
        self.client = APIClient()

    def test_request_auth_code(self):
        """Тест запроса кода авторизации"""
        url = '/api/users/auth/request-code/'
        data = {'phone': '+79111111111'}

        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('code', response.data)
        self.assertEqual(len(response.data['code']), 4)

        # Проверяем, что код сохранился в базе
        auth_code = AuthCode.objects.filter(phone='+79111111111').first()
        self.assertIsNotNone(auth_code)
        self.assertEqual(auth_code.code, response.data['code'])

    def test_request_auth_code_via_get(self):
        """Тест запроса кода через GET"""
        url = '/api/users/auth/request-code/?phone=+79111111111'

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('code', response.data)

    def test_verify_valid_code(self):
        """Тест верификации правильного кода"""
        # Сначала запрашиваем код
        phone = '+79111111111'
        AuthCode.objects.create(phone=phone, code='1234')

        url = '/api/users/auth/verify-code/'
        data = {'phone': phone, 'code': '1234'}

        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['message'], 'Успешная авторизация')
        self.assertIn('invite_code', response.data)

        # Проверяем, что код помечен как использованный
        auth_code = AuthCode.objects.get(phone=phone, code='1234')
        self.assertTrue(auth_code.is_used)

    def test_verify_invalid_code(self):
        """Тест верификации неправильного кода"""
        url = '/api/users/auth/verify-code/'
        data = {'phone': '+79111111111', 'code': '9999'}

        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)

    def test_verify_expired_code(self):
        """Тест верификации устаревшего кода"""
        # Здесь нужно мокать время, но пока простой тест
        phone = '+79111111111'
        AuthCode.objects.create(phone=phone, code='1234', is_used=True)

        url = '/api/users/auth/verify-code/'
        data = {'phone': phone, 'code': '1234'}

        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class ProfileAPITests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(phone='+79111111111')
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_get_profile_authenticated(self):
        """Тест получения профиля авторизованным пользователем"""
        url = '/api/users/profile/'

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['phone'], self.user.phone)
        self.assertEqual(response.data['invite_code'], self.user.invite_code)
        self.assertIn('referrals', response.data)

    def test_activate_invite_code(self):
        """Тест активации инвайт-кода через API"""
        inviter = User.objects.create_user(phone='+79222222222')

        url = '/api/users/profile/'
        data = {'invite_code': inviter.invite_code}

        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('message', response.data)

        # Обновляем пользователя из базы
        self.user.refresh_from_db()
        self.assertEqual(self.user.activated_invite_code, inviter.invite_code)

    def test_get_profile_unauthenticated(self):
        """Тест получения профиля неавторизованным пользователем"""
        client = APIClient()  # Не авторизованный клиент
        url = '/api/users/profile/'

        response = client.get(url)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class IntegrationTests(APITestCase):
    """Интеграционные тесты полного цикла"""

    def test_full_user_flow(self):
        """Тест полного цикла пользователя: регистрация -> активация кода -> проверка рефералов"""
        # 1. Запрос кода авторизации
        phone = '+79111111111'
        request_url = '/api/users/auth/request-code/'
        response = self.client.post(request_url, {'phone': phone}, format='json')
        code = response.data['code']

        # 2. Верификация кода и создание пользователя
        verify_url = '/api/users/auth/verify-code/'
        response = self.client.post(verify_url, {'phone': phone, 'code': code}, format='json')
        user1_invite_code = response.data['invite_code']

        # 3. Создаем второго пользователя
        phone2 = '+79222222222'
        self.client.post(request_url, {'phone': phone2}, format='json')
        auth_code = AuthCode.objects.get(phone=phone2)

        response = self.client.post(verify_url, {'phone': phone2, 'code': auth_code.code}, format='json')
        user2_id = response.data['user_id']

        # 4. Активируем инвайт-код первого пользователя у второго
        # Для этого нам нужно авторизоваться как второй пользователь
        user2 = User.objects.get(id=user2_id)
        client2 = APIClient()
        client2.force_authenticate(user=user2)

        profile_url = '/api/users/profile/'
        response = client2.post(profile_url, {'invite_code': user1_invite_code}, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # 5. Проверяем, что у первого пользователя появился реферал
        user1 = User.objects.get(phone=phone)
        referrals = user1.get_referrals()
        self.assertEqual(referrals.count(), 1)
        self.assertEqual(referrals.first().phone, phone2)