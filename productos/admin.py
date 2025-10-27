from django.contrib import admin
from django.utils.html import format_html
from .models import Categoria, Producto


@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ("nombre", "orden", "descripcion")
    list_editable = ("orden",)
    search_fields = ("nombre",)


@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    list_display = ("miniatura", "nombre", "categoria", "precio", "stock", "destacado")
    list_filter = ("categoria", "destacado")
    search_fields = ("nombre", "descripcion")
    list_editable = ("precio", "stock", "destacado")
    readonly_fields = ("preview",)

    fieldsets = (
        (None, {
            "fields": ("nombre", "categoria", "descripcion", "imagen", "preview", "precio", "stock", "destacado")
        }),
    )

    def miniatura(self, obj):
        if obj.imagen:
            return format_html(
                f'<img src="/media/{obj.imagen}" width="60" height="60" '
                f'style="border-radius:6px; object-fit:contain; background:#f8f6f0; padding:3px;" />'
            )
        return "—"
    miniatura.short_description = "Img"

    def preview(self, obj):
        if obj.imagen:
            return format_html(
                f'<img src="/media/{obj.imagen}" style="max-width:300px; border-radius:8px; '
                f'background:#f6f2e8; padding:8px;" />'
            )
        return "Sin imagen"
    preview.short_description = "Vista previa"
