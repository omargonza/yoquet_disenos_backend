from django.contrib import admin
from django.utils.html import format_html
from .models import Categoria, Producto


# ============================================================
#   ADMIN DE CATEGORÍAS
# ============================================================

@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ("nombre", "orden", "descripcion")
    list_editable = ("orden",)
    search_fields = ("nombre", )


# ============================================================
#   ADMIN DE PRODUCTOS
# ============================================================

@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):

    # 🔥 Hacemos que el NOMBRE sea el link del admin
    list_display = ("miniatura", "nombre", "categoria", "precio", "stock", "destacado")
    list_display_links = ("nombre",)   # ← IMPORTANTE para que abra el formulario

    # Filtros y búsqueda
    list_filter = ("categoria", "destacado")
    search_fields = ("nombre", "descripcion")

    # 🔥 Quitamos list_editable por ahora (lo agregamos después)
    list_editable = ()

    # Vista previa en el formulario
    readonly_fields = ("preview",)

    fieldsets = (
        ("Información del producto", {
            "fields": (
                "nombre",
                "categoria",
                "descripcion",
                "imagen",      # Campo real Cloudinary
                "preview",     # Vista previa
                "precio",
                "stock",
                "destacado",
            )
        }),
    )

    # ============================================================
    #   MINIATURA PARA LA LISTA
    # ============================================================
    def miniatura(self, obj):
        if obj.imagen:
            try:
                return format_html(
                    '<img src="{}" width="60" height="60" '
                    'style="border-radius:6px; object-fit:contain; background:#f8f6f0; padding:3px;" />',
                    obj.imagen.url
                )
            except:
                return "—"
        return "—"

    miniatura.short_description = "Img"

    # ============================================================
    #   PREVIEW EN EL FORMULARIO DE EDICIÓN
    # ============================================================
    def preview(self, obj):
        if obj.imagen:
            try:
                return format_html(
                    '<img src="{}" style="max-width:300px; border-radius:8px; '
                    'background:#f6f2e8; padding:8px;" />',
                    obj.imagen.url
                )
            except:
                return "Sin imagen"
        return "Sin imagen"

    preview.short_description = "Vista previa"
