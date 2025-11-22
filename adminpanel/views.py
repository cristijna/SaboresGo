from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from core.models import Pedido
from core.models import Proveedor


# 🔹 Decorador para requerir usuario administrador (superuser)
def admin_required(view_func):
    return user_passes_test(lambda u: u.is_superuser, login_url='/admin/login/')(view_func)


@login_required
@admin_required
def dashboard(request):
    # Totales de pedidos
    total_pedidos = Pedido.objects.count()
    pedidos_pendientes = Pedido.objects.filter(estado='pendiente').count()
    pedidos_preparando = Pedido.objects.filter(estado='preparando').count()
    pedidos_en_camino = Pedido.objects.filter(estado='en_camino').count()
    pedidos_entregados = Pedido.objects.filter(estado='entregado').count()

    # Totales de proveedores
    total_proveedores = Proveedor.objects.count()
    proveedores_aprobados = Proveedor.objects.filter(aprobado=True).count()
    proveedores_no_aprobados = Proveedor.objects.filter(aprobado=False)

    # Últimos pedidos
    ultimos_pedidos = Pedido.objects.select_related('plato', 'cliente').order_by('-fecha_pedido')[:5]


    context = {
        'total_pedidos': total_pedidos,
        'pedidos_pendientes': pedidos_pendientes,
        'pedidos_preparando': pedidos_preparando,
        'pedidos_en_camino': pedidos_en_camino,
        'pedidos_entregados': pedidos_entregados,
        'total_proveedores': total_proveedores,
        'proveedores_aprobados': proveedores_aprobados,
        'proveedores_no_aprobados': proveedores_no_aprobados,
        'ultimos_pedidos': ultimos_pedidos,
    }
    return render(request, 'core/adminpanel/dashboard.html', context)




@login_required
@admin_required
def aprobar_proveedor(request, proveedor_id):
    proveedor = get_object_or_404(Proveedor, id=proveedor_id)
    proveedor.aprobado = True
    proveedor.save()
    return redirect('dashboard')


@login_required
@admin_required
def rechazar_proveedor(request, proveedor_id):
    proveedor = get_object_or_404(Proveedor, id=proveedor_id)
    proveedor.aprobado = False
    proveedor.save()
    return redirect('dashboard')
