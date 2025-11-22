from django.urls import path
from . import views

app_name = 'adminpanel'  # ← IMPORTANTE

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('aprobar/<int:proveedor_id>/', views.aprobar_proveedor, name='aprobar_proveedor'),
    path('rechazar/<int:proveedor_id>/', views.rechazar_proveedor, name='rechazar_proveedor'),
]
