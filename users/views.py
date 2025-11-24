from django.contrib.auth.models import User
from django.contrib.auth.tokens import default_token_generator
from django.utils.encoding import force_str, force_bytes
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode

from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings

from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated

from .serializers import RegisterSerializer

# =====================================================
#   📌 1. REGISTRO DE USUARIO
# =====================================================
class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]

    def perform_create(self, serializer):
        user = serializer.save()

        if not user.email:
            return

        html = render_to_string("emails/welcome.html", {"username": user.username})

        msg = EmailMultiAlternatives(
            subject="¡Bienvenido a Yoquet Diseños! ✨",
            body="Gracias por registrarte.",
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[user.email],
        )
        msg.attach_alternative(html, "text/html")
        msg.send()


# =====================================================
#   📌 2. SOLICITAR RESET PASSWORD
# =====================================================
class RequestPasswordResetView(generics.GenericAPIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        email = request.data.get("email")

        if not email:
            return Response({"error": "Debe ingresar un correo."}, status=400)

        # Nunca revelar si existe o no
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({"message": "Si el correo existe, enviamos instrucciones."}, status=200)

        uid = urlsafe_base64_encode(force_bytes(user.pk))
        token = default_token_generator.make_token(user)

        reset_url = f"{settings.FRONTEND_URL}/reset-password/{uid}/{token}"

        html = render_to_string("emails/reset_password.html", {"reset_url": reset_url})

        msg = EmailMultiAlternatives(
            subject="Restablecé tu contraseña - Yoquet Diseños",
            body=f"Restablecé tu contraseña aquí: {reset_url}",
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[email],
        )
        msg.attach_alternative(html, "text/html")
        msg.send()

        return Response({"message": "Si el correo existe, enviamos instrucciones."}, status=200)


# =====================================================
#   📌 3. CONFIRMAR RESET PASSWORD
# =====================================================
class PasswordResetConfirmView(generics.GenericAPIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        uidb64 = request.data.get("uid")
        token = request.data.get("token")
        password = request.data.get("password")

        if not password:
            return Response({"error": "Debe ingresar una contraseña."}, status=400)

        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=uid)
        except Exception:
            return Response({"error": "Token inválido."}, status=400)

        if not default_token_generator.check_token(user, token):
            return Response({"error": "Token inválido o expirado."}, status=400)

        user.set_password(password)
        user.save()

        return Response({"redirect": f"{settings.FRONTEND_URL}/reset-success"}, status=200)


# =====================================================
#   📌 4. ENDPOINT /auth/me
# =====================================================
class MeView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        return Response({
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "is_staff": user.is_staff,
            "is_superuser": user.is_superuser,
        })
