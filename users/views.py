from rest_framework import generics, status
from rest_framework.response import Response
from django.utils import timezone
from datetime import timedelta
from .models import User, AuthCode
from .serializers import (
    UserSerializer,
    PhoneAuthSerializer,
    VerifyCodeSerializer,
    ActivateInviteCodeSerializer,
    ProfileSerializer
)
import random
import time
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.contrib.auth import login, authenticate
from django.shortcuts import get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator


@method_decorator(csrf_exempt, name='dispatch')
class UserProfileView(generics.RetrieveAPIView):
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user


@api_view(['GET', 'POST'])
@permission_classes([AllowAny])
@csrf_exempt
def request_auth_code(request):
    if request.method == 'GET':
        # Для тестирования через GET
        phone = request.GET.get('phone')
        if not phone:
            return Response({'error': 'Phone parameter required'}, status=400)

        # Генерируем 4-значный код
        code = str(random.randint(1000, 9999))

        # Сохраняем код в базу (удаляем старые коды для этого номера)
        AuthCode.objects.filter(phone=phone).delete()
        AuthCode.objects.create(phone=phone, code=code)

        # Имитируем задержку отправки SMS
        time.sleep(1)

        print(f"Код {code} отправлен на номер {phone}")

        return Response({
            'message': 'Код отправлен',
            'code': code
        }, status=status.HTTP_200_OK)

    else:  # POST метод
        serializer = PhoneAuthSerializer(data=request.data)
        if serializer.is_valid():
            phone = serializer.validated_data['phone']

            # Генерируем 4-значный код
            code = str(random.randint(1000, 9999))

            # Сохраняем код в базу (удаляем старые коды для этого номера)
            AuthCode.objects.filter(phone=phone).delete()
            AuthCode.objects.create(phone=phone, code=code)

            # Имитируем задержку отправки SMS (1-2 секунды)
            time.sleep(1)

            # В реальном приложении здесь будет отправка SMS
            print(f"Код {code} отправлен на номер {phone}")

            return Response({
                'message': 'Код отправлен',
                'code': code  # Только для разработки!
            }, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'POST'])
@permission_classes([AllowAny])
@csrf_exempt
def verify_code(request):
    if request.method == 'GET':
        # Для тестирования через GET
        phone = request.GET.get('phone')
        code = request.GET.get('code')

        if not phone or not code:
            return Response({'error': 'Phone and code parameters required'}, status=400)

        # Ищем код в базе (действителен 5 минут)
        try:
            auth_code = AuthCode.objects.get(
                phone=phone,
                code=code,
                created_at__gte=timezone.now() - timedelta(minutes=5),
                is_used=False
            )
        except AuthCode.DoesNotExist:
            return Response({'error': 'Неверный или устаревший код'},
                            status=status.HTTP_400_BAD_REQUEST)

        # Помечаем код как использованный
        auth_code.is_used = True
        auth_code.save()

        # Находим или создаем пользователя
        user, created = User.objects.get_or_create(
            phone=phone,
            defaults={'username': f"user_{phone}"}
        )

        # Авторизуем пользователя
        login(request, user)

        return Response({
            'message': 'Успешная авторизация',
            'user_id': user.id,
            'phone': user.phone,
            'invite_code': user.invite_code,
            'is_new_user': created
        }, status=status.HTTP_200_OK)

    else:  # POST метод
        serializer = VerifyCodeSerializer(data=request.data)
        if serializer.is_valid():
            phone = serializer.validated_data['phone']
            code = serializer.validated_data['code']

            # Ищем код в базе (действителен 5 минут)
            try:
                auth_code = AuthCode.objects.get(
                    phone=phone,
                    code=code,
                    created_at__gte=timezone.now() - timedelta(minutes=5),
                    is_used=False
                )
            except AuthCode.DoesNotExist:
                return Response({'error': 'Неверный или устаревший код'},
                                status=status.HTTP_400_BAD_REQUEST)

            # Помечаем код как использованный
            auth_code.is_used = True
            auth_code.save()

            # Находим или создаем пользователя
            user, created = User.objects.get_or_create(
                phone=phone,
                defaults={'username': f"user_{phone}"}
            )

            # Авторизуем пользователя
            login(request, user)

            return Response({
                'message': 'Успешная авторизация',
                'user_id': user.id,
                'phone': user.phone,
                'invite_code': user.invite_code,
                'is_new_user': created
            }, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
@csrf_exempt
def user_profile(request):
    user = request.user

    if request.method == 'GET':
        # Если есть параметр invite_code - активируем его
        invite_code = request.GET.get('invite_code')
        if invite_code:
            success, message = user.activate_invite_code(invite_code)
            if success:
                return Response({
                    'message': message,
                    'activated_invite_code': invite_code
                })
            else:
                return Response({'error': message}, status=status.HTTP_400_BAD_REQUEST)

        # Иначе возвращаем профиль
        serializer = ProfileSerializer(user)
        return Response(serializer.data)

    elif request.method == 'POST':
        serializer = ActivateInviteCodeSerializer(data=request.data)
        if serializer.is_valid():
            invite_code = serializer.validated_data['invite_code']

            success, message = user.activate_invite_code(invite_code)

            if success:
                return Response({
                    'message': message,
                    'activated_invite_code': invite_code
                })
            else:
                return Response({'error': message}, status=status.HTTP_400_BAD_REQUEST)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# Дополнительное view для получения профиля по phone (для тестирования)
@api_view(['GET'])
@permission_classes([AllowAny])
@csrf_exempt
def get_profile_by_phone(request):
    phone = request.GET.get('phone')
    if not phone:
        return Response({'error': 'Phone parameter is required'},
                        status=status.HTTP_400_BAD_REQUEST)

    user = get_object_or_404(User, phone=phone)
    serializer = ProfileSerializer(user)
    return Response(serializer.data)