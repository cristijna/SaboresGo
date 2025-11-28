from datetime import timedelta

from django.contrib.auth.decorators import login_required, user_passes_test
from django.db.models import Sum, F
from django.db.models.functions import TruncDate
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone

from core.models import Pedido, Proveedor


# 🔐 Solo superusuarios pueden ver el panel
def admin_required(view_func):
    return user_passes_test(lambda u: u.is_superuser, login_url='/admin/login/')(view_func)


@login_required
@admin_required
def dashboard(request):
    # -----------------------------
    # 1) MÉTRICAS BÁSICAS PEDIDOS
    # -----------------------------
    total_pedidos = Pedido.objects.count()

    pedidos_pendientes = Pedido.objects.filter(estado='pendiente').count()
    pedidos_preparando = Pedido.objects.filter(estado='preparando').count()
    pedidos_entregados = Pedido.objects.filter(estado='entregado').count()

    # -----------------------------
    # 2) PROVEEDORES / CLIENTES
    # -----------------------------
    total_proveedores = Proveedor.objects.count()
    proveedores_aprobados = Proveedor.objects.filter(aprobado=True).count()
    proveedores_pendientes = Proveedor.objects.filter(aprobado=False).count()

    total_clientes = Pedido.objects.values('cliente').distinct().count()

    # -----------------------------
    # 3) INGRESOS (solo pedidos confirmados)
    # -----------------------------
    hoy = timezone.localdate()
    inicio_mes = hoy.replace(day=1)

    pedidos_confirmados = Pedido.objects.filter(confirmado=True)

    total_ingresos = pedidos_confirmados.aggregate(
        total=Sum(F('plato__precio') * F('cantidad'))
    )['total'] or 0

    ingresos_hoy = pedidos_confirmados.filter(
        fecha_pedido__date=hoy
    ).aggregate(
        total=Sum(F('plato__precio') * F('cantidad'))
    )['total'] or 0

    ingresos_mes = pedidos_confirmados.filter(
        fecha_pedido__date__gte=inicio_mes
    ).aggregate(
        total=Sum(F('plato__precio') * F('cantidad'))
    )['total'] or 0

    # -----------------------------
    # 4) VENTAS ÚLTIMOS 7 DÍAS (gráfico)
    # -----------------------------
    # 4) VENTAS ÚLTIMOS 7 DÍAS (gráfico)
    hoy = timezone.localdate()
    hace_7_dias = hoy - timedelta(days=6)

    # Crear rango fijo de 7 días
    dias_dict = {
        (hace_7_dias + timedelta(days=i)): 0
        for i in range(7)
    }

    ventas = (
        Pedido.objects.filter(confirmado=True)
        .filter(fecha_pedido__date__gte=hace_7_dias)
        .annotate(dia=TruncDate('fecha_pedido'))
        .values('dia')
        .annotate(total=Sum(F('plato__precio') * F('cantidad')))
    )

    # Llenar datos reales
    for v in ventas:
        dia = v['dia']
        if dia in dias_dict:
            dias_dict[dia] = float(v['total'])

    # Preparar arrays para el gráfico
    labels_dias = [d.strftime("%d/%m") for d in dias_dict.keys()]
    data_dias = list(dias_dict.values())



    # -----------------------------
    # 5) TOP 5 PLATOS MÁS VENDIDOS
    # -----------------------------
    top_platos = (
        pedidos_confirmados
        .values('plato__nombre')
        .annotate(total_cantidad=Sum('cantidad'))
        .order_by('-total_cantidad')[:5]
    )

    # -----------------------------
    # 6) ÚLTIMOS PEDIDOS
    # -----------------------------
    ultimos_pedidos = (
        Pedido.objects
        .select_related('plato', 'cliente', 'plato__proveedor')
        .order_by('-fecha_pedido')[:5]
    )

    context = {
        # tarjetas de resumen
        'total_pedidos': total_pedidos,
        'pedidos_pendientes': pedidos_pendientes,
        'pedidos_preparando': pedidos_preparando,
        'pedidos_entregados': pedidos_entregados,

        'total_proveedores': total_proveedores,
        'proveedores_aprobados': proveedores_aprobados,
        'proveedores_pendientes': proveedores_pendientes,
        'total_clientes': total_clientes,

        'total_ingresos': float(total_ingresos),
        'ingresos_hoy': float(ingresos_hoy),
        'ingresos_mes': float(ingresos_mes),

        # gráfico
        'labels_dias': labels_dias,
        'data_dias': data_dias,

        # top platos y últimos pedidos
        'top_platos': top_platos,
        'ultimos_pedidos': ultimos_pedidos,
    }

    return render(request, 'core/adminpanel/dashboard.html', context)


@login_required
@admin_required
def aprobar_proveedor(request, proveedor_id):
    proveedor = get_object_or_404(Proveedor, id=proveedor_id)
    proveedor.aprobado = True
    proveedor.save()
    return redirect('adminpanel:dashboard')


@login_required
@admin_required
def rechazar_proveedor(request, proveedor_id):
    proveedor = get_object_or_404(Proveedor, id=proveedor_id)
    proveedor.aprobado = False
    proveedor.save()
    return redirect('adminpanel:dashboard')


from django.core.paginator import Paginator
from django.db.models import Q
from django.utils.dateparse import parse_date

@login_required
@admin_required
def pedidos_list(request):
    # ------------------------------
    # FILTROS
    # ------------------------------
    estado = request.GET.get('estado')
    proveedor = request.GET.get('proveedor')
    cliente = request.GET.get('cliente')
    fecha_inicio = request.GET.get('fecha_inicio')
    fecha_fin = request.GET.get('fecha_fin')

    pedidos = Pedido.objects.select_related('plato', 'cliente', 'plato__proveedor').order_by('-fecha_pedido')

    # Filtro por estado
    if estado and estado != "":
        pedidos = pedidos.filter(estado=estado)

    # Filtro por proveedor
    if proveedor and proveedor != "":
        pedidos = pedidos.filter(plato__proveedor__id=proveedor)

    # Filtro por cliente (username)
    if cliente and cliente != "":
        pedidos = pedidos.filter(cliente__username__icontains=cliente)

    # Filtro por rango de fechas
    if fecha_inicio:
        fecha_inicio = parse_date(fecha_inicio)
        pedidos = pedidos.filter(fecha_pedido__date__gte=fecha_inicio)

    if fecha_fin:
        fecha_fin = parse_date(fecha_fin)
        pedidos = pedidos.filter(fecha_pedido__date__lte=fecha_fin)

    # ------------------------------
    # PAGINACIÓN
    # ------------------------------
    paginator = Paginator(pedidos, 12)  # 12 pedidos por página
    page_number = request.GET.get('page')
    pedidos_page = paginator.get_page(page_number)

    proveedores = Proveedor.objects.all()

    return render(request, 'core/adminpanel/pedidos_list.html', {
        'pedidos': pedidos_page,
        'proveedores': proveedores,
        # mantener filtros
        'estado': estado or "",
        'cliente': cliente or "",
        'proveedor_selected': proveedor or "",
        'fecha_inicio': fecha_inicio or "",
        'fecha_fin': fecha_fin or "",
    })


@login_required
@admin_required
def clientes_list(request):
    from core.models import Cliente, Pedido

    # Obtener todos los clientes del sistema
    clientes = Cliente.objects.select_related("user").all()

    data = []

    for cliente in clientes:
        pedidos_cliente = Pedido.objects.filter(cliente=cliente)

        total_pedidos = pedidos_cliente.count()
        total_gastado = sum([p.plato.precio * p.cantidad for p in pedidos_cliente])

        ultimo = pedidos_cliente.order_by('-fecha_pedido').first()

        data.append({
            'cliente': cliente,
            'total_pedidos': total_pedidos,
            'total_gastado': total_gastado,
            'ultimo_pedido': ultimo.fecha_pedido if ultimo else None
        })

    return render(request, 'core/adminpanel/clientes_list.html', {
        'clientes': data
    })



@login_required
@admin_required
def cliente_detalle(request, cliente_id):
    from core.models import Cliente, Pedido

    cliente = get_object_or_404(Cliente, id=cliente_id)

    pedidos = Pedido.objects.filter(cliente=cliente).select_related(
        'plato', 'plato__proveedor'
    ).order_by('-fecha_pedido')

    total_gastado = sum([p.plato.precio * p.cantidad for p in pedidos])

    # Top platos más pedidos
    from django.db.models import Sum
    top_platos = (
        pedidos.values('plato__nombre')
               .annotate(total=Sum('cantidad'))
               .order_by('-total')[:5]
    )

    return render(request, 'core/adminpanel/cliente_detalle.html', {
        'cliente': cliente,
        'pedidos': pedidos,
        'total_gastado': total_gastado,
        'top_platos': top_platos,
    })



@login_required
@admin_required
def proveedores_list(request):
    proveedores = Proveedor.objects.all()

    data = []

    for pr in proveedores:
        pedidos = Pedido.objects.filter(plato__proveedor=pr)

        total_pedidos = pedidos.count()
        total_ingresos = sum([p.plato.precio * p.cantidad for p in pedidos])
        platos_count = pr.platos.count()


        data.append({
            'proveedor': pr,
            'total_pedidos': total_pedidos,
            'total_ingresos': total_ingresos,
            'platos_count': platos_count,
        })

    return render(request, 'core/adminpanel/proveedores_list.html', {
        'proveedores': data
    })


@login_required
@admin_required
def proveedor_detalle(request, proveedor_id):
    proveedor = get_object_or_404(Proveedor, id=proveedor_id)

    pedidos = Pedido.objects.filter(
        plato__proveedor=proveedor
    ).select_related('plato', 'cliente')

    total_ingresos = sum([p.plato.precio * p.cantidad for p in pedidos])

    # Top platos del proveedor
    from django.db.models import Sum
    top_platos = (
        pedidos.values('plato__nombre')
        .annotate(total_vendido=Sum('cantidad'))
        .order_by('-total_vendido')[:5]
    )

    return render(request, 'core/adminpanel/proveedor_detalle.html', {
        'proveedor': proveedor,
        'pedidos': pedidos,
        'total_ingresos': total_ingresos,
        'top_platos': top_platos,
    })


@login_required
def cambiar_estado_pedido(request, pedido_id, nuevo_estado):
    pedido = get_object_or_404(Pedido, id=pedido_id)

    # si pasa de pendiente → preparando, entonces se confirma
    if pedido.estado == "pendiente" and nuevo_estado == "preparando":
        pedido.confirmado = True

    pedido.estado = nuevo_estado
    pedido.save()

    return redirect(request.META.get('HTTP_REFERER', 'adminpanel:pedidos_list'))

@login_required
def pedidos_proveedor_panel(request):
    # Validar que el usuario sea proveedor
    if not hasattr(request.user, "proveedor"):
        return redirect("core:catalogo")

    proveedor = request.user.proveedor

    # Filtrar solo pedidos de sus platos
    pedidos = Pedido.objects.filter(
        plato__proveedor=proveedor
    ).select_related("cliente", "plato").order_by("-fecha_pedido")

    return render(request, "core/proveedor/pedidos_panel.html", {
        "pedidos": pedidos,
        "proveedor": proveedor
    })
