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


# =======================
#   REGISTRO
# =======================
class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]


    def perform_create(self, serializer):
        user = serializer.save()

        # HTML de bienvenida
        html_message = render_to_string("emails/welcome.html", {
            "username": user.username
        })

        email = EmailMultiAlternatives(
            subject="¡Bienvenido a Yoquet Diseños ✨!",
            body="Gracias por registrarte en Yoquet Diseños.",
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[user.email]
        )
        email.attach_alternative(html_message, "text/html")
        email.send()


# =======================
#   SOLICITAR RESET (EMAIL)
# =======================
class RequestPasswordResetView(generics.GenericAPIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        email = request.data.get("email")

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({"error": "No existe un usuario con ese correo."}, status=400)

        # 🔗 Generar link de recuperación
        uid = urlsafe_base64_encode(str(user.pk).encode())
        token = PasswordResetTokenGenerator().make_token(user)

        reset_url = f"{settings.FRONTEND_URL}/reset-password/{uid}/{token}"

        # 📧 Renderizar HTML del email
        html_content = render_to_string(
            "emails/reset_password.html",
            {"reset_url": reset_url}
        )

        # 📧 Crear mensaje
        email_message = EmailMultiAlternatives(
            subject="Restablecé tu contraseña - Yoquet Diseños",
            body=f"Para restablecer tu contraseña, hacé clic acá: {reset_url}",
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[email],
        )
        email_message.attach_alternative(html_content, "text/html")

        # 🚀 Enviar
        email_message.send()

        return Response({"message": "Enviamos un correo con instrucciones ✨"}, status=200)


# ===============================
#   CONFIRMAR NUEVA CONTRASEÑA
# ===============================
class PasswordResetConfirmView(generics.GenericAPIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        uidb64 = request.data.get("uid")
        token = request.data.get("token")
        password = request.data.get("password")

        if not password:
            return Response({"error": "Contraseña requerida"}, status=400)

        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=uid)
        except Exception:
            return Response({"error": "Token inválido"}, status=400)

        if not default_token_generator.check_token(user, token):
            return Response({"error": "Token inválido o expirado"}, status=400)

        # ✔ Cambiar contraseña
        user.set_password(password)
        user.save()

        return Response({"redirect": f"{settings.FRONTEND_URL}/reset-success"})

