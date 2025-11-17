# productos/models.py
from django.db import models
from cloudinary.models import CloudinaryField

class Categoria(models.Model):
    nombre = models.CharField(max_length=100, unique=True)
    descripcion = models.TextField(blank=True)
    creado = models.DateTimeField(auto_now_add=True)
    orden = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['nombre']

    def __str__(self):
        return self.nombre



class Producto(models.Model):
    categoria = models.ForeignKey(Categoria, related_name='productos', on_delete=models.CASCADE)
    nombre = models.CharField(max_length=550)
    descripcion = models.TextField(blank=True)
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.PositiveIntegerField(default=0)
    destacado = models.BooleanField(default=False)

    imagen = CloudinaryField(
        "imagen",
        folder="yoquet/productos",
        null=True,
        blank=True
    )

    creado = models.DateTimeField(auto_now_add=True)
    actualizado = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-destacado', 'nombre']

    def __str__(self):
        return self.nombre
