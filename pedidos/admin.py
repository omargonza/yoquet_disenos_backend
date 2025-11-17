from django.contrib import admin
from .models import Pedido, PedidoItem

class PedidoItemInline(admin.TabularInline):
    model = PedidoItem
    extra = 0

@admin.register(Pedido)
class PedidoAdmin(admin.ModelAdmin):
    list_display = ("id", "usuario", "total", "creado")
    list_filter = ("creado",)
    search_fields = ("usuario__username", "email", "nombre")
    inlines = [PedidoItemInline]
