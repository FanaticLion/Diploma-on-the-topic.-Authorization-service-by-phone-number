from rest_framework import generics
from .models import User
from .serializers import UserSerializer


class UserProfileView(generics.RetrieveAPIView):
    serializer_class = UserSerializer

    def get_object(self):
        return self.request.user