from django.contrib import admin
from django.urls import path,include
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from django.views.generic import TemplateView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/users/', include('users.urls')),
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('', TemplateView.as_view(template_name='home.html'), name='home'),
    path('login/', TemplateView.as_view(template_name='login.html'), name='login'),
    path('profile/', TemplateView.as_view(template_name='profile.html'), name='user-profile'),
    path('admin/', admin.site.urls),
    path('api/users/', include('users.urls'))
]
