from rest_framework import serializers
from django.conf import settings
from .models import Categoria, Producto
import re


def clean_cloudinary_path(path: str) -> str:
    if not path:
        return ""

    if path.startswith("http://") or path.startswith("https://"):
        return path

    path = path.strip().lstrip("/")

    # Normalizaciones
    path = re.sub(r"(image/upload/)+", "image/upload/", path)
    path = path.replace("yoquet/", "")
    path = path.replace("media/", "")
    path = re.sub(r"^productos/", "", path)

    return path


def build_cloudinary_final_url(path: str) -> str:
    if not path:
        return None

    if "res.cloudinary.com" in path:
        return path

    cloud_name = settings.CLOUDINARY_STORAGE.get("CLOUD_NAME")

    return f"https://res.cloudinary.com/{cloud_name}/image/upload/{path}"


# =============================================
#   SERIALIZA CATEGORÍAS
# =============================================
class CategoriaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Categoria
        fields = ["id", "nombre", "descripcion"]


# =============================================
#   SERIALIZA PRODUCTOS
# =============================================
class ProductoListSerializer(serializers.ModelSerializer):
    categoria_nombre = serializers.CharField(source="categoria.nombre", read_only=True)
    imagen = serializers.SerializerMethodField()

    class Meta:
        model = Producto
        fields = [
            "id",
            "nombre",
            "precio",
            "imagen",
            "categoria_nombre",
        ]

    def get_imagen(self, obj):
        # Protección completa
        try:
            raw = getattr(obj, "imagen", None)
        except Exception:
            return None

        if not raw:
            return None

        # Caso Cloudinary real
        try:
            url = raw.url
            if url:
                return url
        except Exception:
            pass

        # Convertir a string
        try:
            raw = str(raw).strip()
        except Exception:
            return None

        # Si ya es URL absoluta
        if raw.startswith("http://") or raw.startswith("https://"):
            return raw

        # Limpiar y construir URL final
        cleaned = clean_cloudinary_path(raw)
        return build_cloudinary_final_url(cleaned)


class ProductoDetailSerializer(serializers.ModelSerializer):
    categoria = CategoriaSerializer(read_only=True)

    categoria_id = serializers.PrimaryKeyRelatedField(
        source="categoria",
        queryset=Categoria.objects.all(),
        write_only=True
    )

    imagen = serializers.SerializerMethodField()

    categoria_nombre = serializers.CharField(
        source="categoria.nombre",
        read_only=True
    )

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
            "categoria_nombre",
        ]

    def get_imagen(self, obj):
        # Protección completa
        try:
            raw = getattr(obj, "imagen", None)
        except Exception:
            return None

        if not raw:
            return None

        # Caso Cloudinary real
        try:
            url = raw.url
            if url:
                return url
        except Exception:
            pass

        # Convertir a string
        try:
            raw = str(raw).strip()
        except Exception:
            return None

        # Si ya es URL absoluta
        if raw.startswith("http://") or raw.startswith("https://"):
            return raw

        # Limpiar y construir URL final
        cleaned = clean_cloudinary_path(raw)
        return build_cloudinary_final_url(cleaned)
