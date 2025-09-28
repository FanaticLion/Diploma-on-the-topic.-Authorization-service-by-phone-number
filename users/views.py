from rest_framework import generics, status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.utils import timezone
from datetime import timedelta
from .models import User, AuthCode
from .serializers import UserSerializer, PhoneAuthSerializer, VerifyCodeSerializer
import random


class UserProfileView(generics.RetrieveAPIView):
    serializer_class = UserSerializer

    def get_object(self):
        return self.request.user



@api_view(['POST'])
def request_auth_code(request):
    serializer = PhoneAuthSerializer(data=request.data)
    if serializer.is_valid():
        phone = serializer.validated_data['phone']

        # Генерируем 4-значный код
        code = str(random.randint(1000, 9999))

        # Сохраняем код в базу (временное хранилище)
        AuthCode.objects.filter(phone=phone).delete()  # Удаляем старые коды
        AuthCode.objects.create(phone=phone, code=code)

        # Имитируем задержку отправки SMS (1-2 секунды)
        print(f"Код {code} отправлен на номер {phone}")

        return Response({'message': 'Код отправлен'}, status=status.HTTP_200_OK)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
def verify_code(request):
    serializer = VerifyCodeSerializer(data=request.data)
    if serializer.is_valid():
        phone = serializer.validated_data['phone']
        code = serializer.validated_data['code']

        # Ищем код в базе
        try:
            auth_code = AuthCode.objects.get(
                phone=phone,
                code=code,
                created_at__gte=timezone.now() - timedelta(minutes=5)  # Код действителен 5 минут
            )
        except AuthCode.DoesNotExist:
            return Response({'error': 'Неверный код'}, status=status.HTTP_400_BAD_REQUEST)

        # Находим или создаем пользователя
        user, created = User.objects.get_or_create(
            phone=phone,
            defaults={'username': f"user_{phone}"}
        )

        # Генерируем инвайт-код при первой авторизации
        if created and not user.invite_code:
            user.generate_invite_code()

        # Удаляем использованный код
        auth_code.delete()

        return Response({
            'message': 'Успешная авторизация',
            'user_id': user.id,
            'phone': user.phone,
            'invite_code': user.invite_code,
            'is_new_user': created
        }, status=status.HTTP_200_OK)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)