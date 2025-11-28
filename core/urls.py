from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    path('', views.catalogo, name='catalogo'),

    # Menú semanal
    path('menu-semanal/', views.menu_semanal, name='menu_semanal'),
    path('menu-semanal/select/<str:dia>/', views.menu_semanal_select, name='menu_semanal_select'),

    path('plato/<int:pk>/', views.plato_detalle, name='plato_detalle'),

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
    path('proveedor/pedidos-panel/', views.pedidos_proveedor_panel, name='pedidos_proveedor_panel'),
    path(
    'proveedor/pedido/<int:pedido_id>/estado/<str:nuevo_estado>/',
    views.proveedor_cambiar_estado_pedido,
    name='proveedor_cambiar_estado_pedido'
),



    # Cliente – Pedidos (Carrito)
    path('cliente/pedidos/', views.pedido_list, name='pedido_list'),
    path('cliente/pedidos/crear/', views.pedido_create, name='pedido_create'),
    path('cliente/pedidos/<int:pk>/editar/', views.pedido_edit, name='pedido_edit'),
    path('cliente/pedidos/<int:pk>/eliminar/', views.pedido_delete, name='pedido_delete'),
    path('mis-pedidos/', views.mis_pedidos, name='mis_pedidos'),

    # Cliente – Pedido Detalle (HISTÓRICO)
    path('cliente/pedidos/<int:pk>/', views.pedido_detalle, name='pedido_detalle'),

    # Pedido rápido
    path('pedido/rapido/<int:pk>/', views.pedido_rapido, name='pedido_rapido'),

    # Mi Perfil
    path('miperfil/', views.miperfil, name='miperfil'),
]
