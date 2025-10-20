from rest_framework import serializers
from .models import Categoria, Producto

class CategoriaSerializer(serializers.ModelSerializer):
    class Meta:
        model=Categoria
        fields=['id','nombre','descripcion']

class ProductoSerializer(serializers.ModelSerializer):
    categoria=CategoriaSerializer(read_only=True)
    categoria_id=serializers.PrimaryKeyRelatedField(source='categoria', queryset=Categoria.objects.all(), write_only=True)
    class Meta:
        model=Producto
        fields=['id','nombre','descripcion','precio','stock','destacado','imagen','categoria','categoria_id']
