from rest_framework import serializers
from django.conf import settings
from .models import Categoria, Producto
import re


def clean_cloudinary_path(path: str) -> str:
    """
    Normaliza rutas dañadas.
    """
    if not path:
        return ""

    if path.startswith("http://") or path.startswith("https://"):
        return path

    path = path.strip().lstrip("/")

    path = re.sub(r"(image/upload/)+", "image/upload/", path)
    path = path.replace("yoquet/", "")
    path = path.replace("media/", "")
    path = re.sub(r"^productos/", "", path)

    return path


def build_cloudinary_final_url(path: str) -> str:
    """
    Devuelve siempre una URL Cloudinary válida y segura.
    """
    if not path:
        return None

    if "res.cloudinary.com" in path:
        return path

    # usar cloud_name desde settings (seguro)
    cloud_name = settings.CLOUDINARY_STORAGE.get("CLOUD_NAME")

    return f"https://res.cloudinary.com/{cloud_name}/image/upload/{path}"


class CategoriaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Categoria
        fields = ["id", "nombre", "descripcion"]


class ProductoSerializer(serializers.ModelSerializer):
    categoria = CategoriaSerializer(read_only=True)
    categoria_id = serializers.PrimaryKeyRelatedField(
        source="categoria", queryset=Categoria.objects.all(), write_only=True
    )

    imagen = serializers.SerializerMethodField()

    class Meta:
        model = Producto
        fields = [
            "id",
            "nombre",
            "descripcion",
            "precio",
            "stock",
            "destacado",
            "imagen",
            "categoria",
            "categoria_id",
        ]

    def get_imagen(self, obj):
        raw = obj.imagen

        if not raw:
            return None

        # Caso Cloudinary real
        try:
            url = raw.url
            if url:
                return url
        except Exception:
            pass

        raw = str(raw).strip()

        # URL absoluta
        if raw.startswith("http://") or raw.startswith("https://"):
            return raw

        # Limpiar
        cleaned = clean_cloudinary_path(raw)

        # Generar final segura
        return build_cloudinary_final_url(cleaned)
