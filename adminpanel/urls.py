from django.urls import path
from . import views

app_name = 'adminpanel'  # ← IMPORTANTE

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('pedidos/', views.pedidos_list, name='pedidos_list'),
    path('clientes/', views.clientes_list, name='clientes_list'),
    path('clientes/<int:cliente_id>/', views.cliente_detalle, name='cliente_detalle'),
    path('proveedores/', views.proveedores_list, name='proveedores_list'),
    path('proveedores/<int:proveedor_id>/', views.proveedor_detalle, name='proveedor_detalle'),
    path('aprobar/<int:proveedor_id>/', views.aprobar_proveedor, name='aprobar_proveedor'),
    path('rechazar/<int:proveedor_id>/', views.rechazar_proveedor, name='rechazar_proveedor'),
    path('pedidos/<int:pedido_id>/estado/<str:nuevo_estado>/', 
     views.cambiar_estado_pedido, 
     name='cambiar_estado_pedido'),

]


