from django.urls import path
from . import views

urlpatterns = [
    # API endpoints
    path('auth/request-code/', views.request_auth_code, name='request-auth-code'),
    path('auth/verify-code/', views.verify_code, name='verify-code'),
    path('profile/', views.user_profile, name='user-profile'),
    path('profile/by-phone/', views.get_profile_by_phone, name='profile-by-phone'),
    path('profile/activate-invite/', views.activate_invite_code, name='activate-invite'),

    # Class-based view
    path('profile/me/', views.UserProfileView.as_view(), name='user-profile-me'),
]