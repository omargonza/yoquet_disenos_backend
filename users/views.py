from django.contrib.auth.models import User
from django.contrib.auth.tokens import default_token_generator, PasswordResetTokenGenerator
from django.utils.encoding import force_str
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode

from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings

from rest_framework import generics, permissions, status
from rest_framework.response import Response

from .serializers import RegisterSerializer


# =============================================
#  REGISTRO DE USUARIO
# =============================================
class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]

    def perform_create(self, serializer):
        user = serializer.save()

        # Evitar enviar mails sin email
        if not user.email:
            return

        html = render_to_string("emails/welcome.html", {"username": user.username})

        msg = EmailMultiAlternatives(
            subject="¡Bienvenido a Yoquet Diseños! ✨",
            body="Gracias por registrarte.",
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[user.email]
        )
        msg.attach_alternative(html, "text/html")
        msg.send()


# =============================================
#  SOLICITAR RESET DE CONTRASEÑA
# =============================================
class RequestPasswordResetView(generics.GenericAPIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        email = request.data.get("email")

        if not email:
            return Response({"error": "Debe ingresar un correo."}, status=400)

        # Seguridad: no revelar si el correo existe o no
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response(
                {"message": "Si el correo existe, enviamos instrucciones."},
                status=200
            )

        # Construcción segura del link
        uid = urlsafe_base64_encode(str(user.pk).encode())
        token = PasswordResetTokenGenerator().make_token(user)
        reset_url = f"{settings.FRONTEND_URL}/reset-password/{uid}/{token}"

        # Render HTML
        html = render_to_string("emails/reset_password.html", {"reset_url": reset_url})

        msg = EmailMultiAlternatives(
            subject="Restablecé tu contraseña - Yoquet Diseños",
            body=f"Restablecé tu contraseña aquí: {reset_url}",
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[email],
        )
        msg.attach_alternative(html, "text/html")
        msg.send()

        return Response(
            {"message": "Si el correo existe, enviamos instrucciones."},
            status=200
        )


# =============================================
#  CONFIRMAR RESET DE CONTRASEÑA
# =============================================
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

        return Response(
            {"redirect": f"{settings.FRONTEND_URL}/reset-success"},
            status=200
        )
