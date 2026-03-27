from django.urls import path
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
)
from .views import RegisterView, MeView, LogoutView

urlpatterns = [
    # ── JWT Auth ────────────────────────────────────────────────
    path('login/',         TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('logout/',        LogoutView.as_view(),          name='logout'),
    path('token/refresh/', TokenRefreshView.as_view(),    name='token_refresh'),
    path('token/verify/',  TokenVerifyView.as_view(),     name='token_verify'),

    # ── User ────────────────────────────────────────────────────
    path('register/', RegisterView.as_view(), name='register'),
    path('me/',       MeView.as_view(),       name='me'),
]
