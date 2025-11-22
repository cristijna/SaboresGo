from django.contrib import admin
from .models import Proveedor, Plato, Pedido

@admin.register(Proveedor)
class ProveedorAdmin(admin.ModelAdmin):
    list_display = ('empresa', 'user')

@admin.register(Plato)
class PlatoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'proveedor', 'precio', 'creado_en')
    list_filter = ('proveedor',)

@admin.register(Pedido)
class PedidoAdmin(admin.ModelAdmin):
    list_display = ('id', 'cliente', 'plato', 'cantidad', 'estado', 'creado_en')
    list_filter = ('estado',)
