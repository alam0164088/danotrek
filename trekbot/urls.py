from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from accounts.views import AuthViewSet

router = DefaultRouter()
router.register(r'auth', AuthViewSet, basename='auth')

from django.contrib import admin
from django.urls import path, include
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from rest_framework.routers import DefaultRouter
from accounts.views import AuthViewSet

router = DefaultRouter()
router.register(r'auth', AuthViewSet, basename='auth')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include(router.urls)),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]



# Map actions to specific endpoints
urlpatterns += [
    path('api/auth/register/', AuthViewSet.as_view({'post': 'register'})),
    path('api/auth/login/', AuthViewSet.as_view({'post': 'login'})),
    path('api/auth/verify-otp/', AuthViewSet.as_view({'post': 'verify_otp'})),
]