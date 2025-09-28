from django.urls import path
from . import views

urlpatterns = [
    path('profile/', views.UserProfileView.as_view(), name='user-profile'),
    path('auth/', views.request_auth_code, name='request-auth-code'),
    path('verify/', views.verify_code, name='verify-code'),
]