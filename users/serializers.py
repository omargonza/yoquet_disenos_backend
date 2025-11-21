from django.contrib.auth.models import User
from rest_framework import serializers
from django.core.validators import validate_email
from django.db.models import Q


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)
    email = serializers.EmailField(required=True)

    class Meta:
        model = User
        fields = ("username", "email", "password")

    def validate_email(self, value):
        value = value.lower().strip()

        if User.objects.filter(email__iexact=value).exists():
            raise serializers.ValidationError("El email ya está registrado.")

        return value

    def validate_username(self, value):
        if User.objects.filter(username__iexact=value).exists():
            raise serializers.ValidationError("Este nombre de usuario ya existe.")

        return value

    def create(self, validated_data):
        # Sanitizar
        username = validated_data["username"].strip()
        email = validated_data["email"].lower().strip()
        password = validated_data["password"]

        user = User.objects.create_user(
            username=username,
            email=email,
            password=password
        )
        return user
