from rest_framework import serializers
from .models import Categoria, Producto

class CategoriaSerializer(serializers.ModelSerializer):
    class Meta:
        model=Categoria
        fields=['id','nombre','descripcion']

class ProductoSerializer(serializers.ModelSerializer):
    categoria = CategoriaSerializer(read_only=True)
    categoria_id = serializers.PrimaryKeyRelatedField(
        source='categoria', queryset=Categoria.objects.all(), write_only=True
    )

    imagen = serializers.SerializerMethodField()  # 👈 CAMBIO IMPORTANTE

    class Meta:
        model = Producto
        fields = [
            'id',
            'nombre',
            'descripcion',
            'precio',
            'stock',
            'destacado',
            'imagen',       # devuelve URL completa
            'categoria',
            'categoria_id',
        ]

    def get_imagen(self, obj):
        """
        Devuelve la URL completa de la imagen.
        Con Cloudinary: secure_url CDN ✅
        En local: http://127.0.0.1:8000/media/... ✅
        """
        try:
            return obj.imagen.url  # Cloudinary o Media local
        except:
            return None
