from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    # Público / Catálogo
    path('', views.catalogo, name='catalogo'),
    path('plato/<int:id>/', views.plato_detalle, name='plato_detalle'),

    # Autenticación
    path('register/', views.register, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),

    # Proveedor – CRUD de platos
    path('proveedores/', views.proveedores, name='proveedores'),
    path('proveedor/platos/', views.plato_list, name='plato_list'),
    path('proveedor/platos/crear/', views.plato_create, name='plato_create'),
    path('proveedor/platos/<int:pk>/editar/', views.plato_edit, name='plato_edit'),
    path('proveedor/platos/<int:pk>/eliminar/', views.plato_delete, name='plato_delete'),

    # Cliente – Pedidos (Carrito)
    path('cliente/pedidos/', views.pedido_list, name='pedido_list'),
    path('cliente/pedidos/crear/', views.pedido_create, name='pedido_create'),
    path('cliente/pedidos/<int:pk>/editar/', views.pedido_edit, name='pedido_edit'),
    path('cliente/pedidos/<int:pk>/eliminar/', views.pedido_delete, name='pedido_delete'),
    path('mis-pedidos/', views.mis_pedidos, name='mis_pedidos'),


    # Cliente – Pedido Detalle (HISTÓRICO)
    path('cliente/pedidos/<int:pk>/', views.pedido_detalle, name='pedido_detalle'),

    # Pedido rápido (1 clic)
    path('pedido/rapido/<int:pk>/', views.pedido_rapido, name='pedido_rapido'),
]
