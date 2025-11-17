# productos/serializers.py
from rest_framework import serializers
from .models import Categoria, Producto
import re


def clean_cloudinary_path(path: str) -> str:
    """
    Normaliza rutas que vienen con duplicado de carpetas,
    errores comunes, prefijos basura y rutas absolutas antiguas.
    """

    if not path:
        return ""

    # Si es una URL válida → retornarla directamente
    if path.startswith("http://") or path.startswith("https://"):
        return path

    # Limpieza general
    path = path.strip().lstrip("/")

    # Quitar prefijos repetidos
    path = re.sub(r"(image/upload/)+", "image/upload/", path)

    # Quitar carpetas inapropiadas agregadas por migraciones viejas
    path = path.replace("yoquet/", "")
    path = path.replace("media/", "")
    path = re.sub(r"^productos/", "", path)

    return path


def build_cloudinary_final_url(path: str) -> str:
    """
    Construye la URL final segura a Cloudinary.
    Evita duplicar dominio o carpeta de delivery.
    """
    if not path:
        return None

    # Si ya es una URL Cloudinary segura → devolverla
    if "res.cloudinary.com" in path:
        return path

    # Usar dominio oficial como CDN
    cloud_name = "dfkyxmjnx"

    return f"https://res.cloudinary.com/{cloud_name}/image/upload/{path}"


class CategoriaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Categoria
        fields = ["id", "nombre", "descripcion"]


class ProductoSerializer(serializers.ModelSerializer):
    categoria = CategoriaSerializer(read_only=True)

    # Para crear o editar
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
        """
        ULTRA RESISTENTE:
        - CloudinaryStorage
        - URL absoluta
        - Rutas dañadas
        - Rutas locales
        """
        raw = obj.imagen

        if not raw:
            return None

        # Caso 1: Cloudinary real
        try:
            url = raw.url
            if url:
                return url
        except Exception:
            pass

        # Caso 2: String normal
        raw = str(raw).strip()

        # Caso 3: URL ya completa
        if raw.startswith("http://") or raw.startswith("https://"):
            return raw

        # Caso 4: Limpiar rutas viejas
        cleaned = clean_cloudinary_path(raw)

        # Caso 5: Armar URL Cloudinary segura
        return build_cloudinary_final_url(cleaned)
