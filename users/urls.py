from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from .views import (
    RegisterView,
    RequestPasswordResetView,
    PasswordResetConfirmView,
    MeView,
)

urlpatterns = [
    # Registro
    path("register/", RegisterView.as_view(), name="register"),

    # JWT
    path("login/", TokenObtainPairView.as_view(), name="login"),
    path("refresh/", TokenRefreshView.as_view(), name="token_refresh"),

    # Password reset
    path("password-reset/", RequestPasswordResetView.as_view(), name="password_reset"),
    path("password-reset-confirm/", PasswordResetConfirmView.as_view(), name="password_reset_confirm"),

    # Usuario actual
    path("me/", MeView.as_view(), name="me"),
]
