from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from .forms import UserRegisterForm, ProveedorProfileForm, LoginForm, PlatoForm, PedidoForm
from .models import Proveedor, Plato, Pedido
from django.contrib.auth.models import User

def _is_proveedor(user):
    return hasattr(user, 'proveedor')


def register(request):
    if request.method == 'POST':
        uform = UserRegisterForm(request.POST)
        pform = ProveedorProfileForm(request.POST, request.FILES)
        rol = request.POST.get('rol')  # 'proveedor' o 'cliente'
        if uform.is_valid() and (rol == 'cliente' or pform.is_valid()):
            user = uform.save(commit=False)
            user.set_password(uform.cleaned_data['password'])
            user.save()
            if rol == 'proveedor':
                Proveedor.objects.create(user=user,
                                        empresa=pform.cleaned_data['empresa'],
                                        descripcion=pform.cleaned_data.get('descripcion'),
                                        logo=pform.cleaned_data.get('logo'))
            messages.success(request, 'Registro completado. Inicia sesión.')
            return redirect('core:login')
    else:
        uform = UserRegisterForm()
        pform = ProveedorProfileForm()
    return render(request, 'core/register.html', {'uform': uform, 'pform': pform})

def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('core:catalogo')
    else:
        form = LoginForm()
    return render(request, 'core/login.html', {'form': form})

def logout_view(request):
    logout(request)
    return redirect('core:catalogo')

def catalogo(request):
    proveedores = Proveedor.objects.all().prefetch_related('platos')

    # Determinar si el usuario es proveedor
    is_proveedor = False
    latest_pedido = None

    if request.user.is_authenticated:
        # si es proveedor lo mantenemos igual
        is_proveedor = hasattr(request.user, 'proveedor')

        # buscar el último pedido confirmado O con estado que tu quieras
        latest_pedido = (
            Pedido.objects
            .filter(cliente=request.user)
            .order_by('-creado_en')
            .first()
        )

    return render(request, 'core/catalogo.html', {
        'proveedores': proveedores,
        'is_proveedor': is_proveedor,
        'latest_pedido': latest_pedido
    })

# --- Proveedor: CRUD Platos ---
@login_required
@user_passes_test(_is_proveedor)
def plato_list(request):
    proveedor = request.user.proveedor
    platos = Plato.objects.filter(proveedor=proveedor)
    return render(request, 'core/proveedor/plato_list.html', {'platos': platos})

@login_required
@user_passes_test(_is_proveedor)
def plato_create(request):
    proveedor = request.user.proveedor
    if request.method == 'POST':
        form = PlatoForm(request.POST, request.FILES)
        if form.is_valid():
            plato = form.save(commit=False)
            plato.proveedor = proveedor
            plato.save()
            messages.success(request, 'Plato creado.')
            return redirect('core:plato_list')
    else:
        form = PlatoForm()
    return render(request, 'core/proveedor/plato_form.html', {'form': form})

@login_required
@user_passes_test(_is_proveedor)
def plato_edit(request, pk):
    proveedor = request.user.proveedor
    plato = get_object_or_404(Plato, pk=pk, proveedor=proveedor)
    if request.method == 'POST':
        form = PlatoForm(request.POST, request.FILES, instance=plato)
        if form.is_valid():
            form.save()
            messages.success(request, 'Plato actualizado.')
            return redirect('core:plato_list')
    else:
        form = PlatoForm(instance=plato)
    return render(request, 'core/proveedor/plato_form.html', {'form': form, 'plato': plato})

@login_required
@user_passes_test(_is_proveedor)
def plato_delete(request, pk):
    proveedor = request.user.proveedor
    plato = get_object_or_404(Plato, pk=pk, proveedor=proveedor)
    if request.method == 'POST':
        plato.delete()
        messages.success(request, 'Plato eliminado.')
        return redirect('core:plato_list')
    return render(request, 'core/proveedor/plato_confirm_delete.html', {'plato': plato})

# --- Cliente: CRUD Pedidos ---
@login_required
def pedido_list(request):
    pedidos = Pedido.objects.filter(cliente=request.user, confirmado=False).select_related('plato', 'plato__proveedor')

    # Confirmar todos los pedidos del carrito
    if request.method == 'POST' and 'confirmar_carrito' in request.POST:
        pedidos.update(confirmado=True, estado='pendiente')
        messages.success(request, 'Tu pedido fue confirmado. El restaurante comenzará la preparación.')
        return redirect('core:pedido_list')

    # ✅ Calcular total del carrito correctamente
    total_carrito = sum(p.plato.precio for p in pedidos)

    return render(request, 'core/cliente/pedido_list.html', {
        'pedidos': pedidos,
        'total_carrito': total_carrito
    })


@login_required
def pedido_create(request):
    if request.method == 'POST':
        form = PedidoForm(request.POST)
        if form.is_valid():
            pedido = form.save(commit=False)
            pedido.cliente = request.user
            pedido.save()
            messages.success(request, 'Pedido creado.')
            return redirect('core:pedido_list')
    else:
        form = PedidoForm()
    return render(request, 'core/cliente/pedido_form.html', {'form': form})

@login_required
def pedido_edit(request, pk):
    pedido = get_object_or_404(Pedido, pk=pk, cliente=request.user)
    if request.method == 'POST':
        form = PedidoForm(request.POST, instance=pedido)
        if form.is_valid():
            form.save()
            messages.success(request, 'Pedido actualizado.')
            return redirect('core:pedido_list')
    else:
        form = PedidoForm(instance=pedido)
    return render(request, 'core/cliente/pedido_form.html', {'form': form, 'pedido': pedido})

@login_required
def pedido_delete(request, pk):
    pedido = get_object_or_404(Pedido, pk=pk, cliente=request.user)
    if request.method == 'POST':
        pedido.delete()
        messages.success(request, 'Pedido eliminado.')
        return redirect('core:pedido_list')
    return render(request, 'core/cliente/pedido_confirm_delete.html', {'pedido': pedido})

def proveedores(request):
    proveedores = Proveedor.objects.filter(aprobado=True)
    return render(request, 'core/proveedores.html', {'proveedores': proveedores})

def plato_detalle(request, pk):
    plato = get_object_or_404(Plato, pk=pk)
    return render(request, 'core/plato_detalle.html', {'plato': plato})

@login_required
def pedido_rapido(request, pk):
    plato = get_object_or_404(Plato, pk=pk)

    if request.method == 'POST':
        cantidad = int(request.POST.get('cantidad', 1))

        Pedido.objects.create(
            cliente=request.user,
            plato=plato,
            cantidad=cantidad,
            estado='pendiente',
            direccion="",       
            confirmado=False
        )

        messages.success(request, 'Plato añadido al carrito.')
        return redirect('core:pedido_list')

    return redirect('core:plato_detalle', pk=pk)

from django.shortcuts import render, get_object_or_404
from .models import Plato

@login_required
def pedido_detalle(request, pk):
    pedido = get_object_or_404(Pedido, pk=pk, cliente=request.user)
    return render(request, 'core/cliente/pedido_detalle.html', {'pedido': pedido})


@login_required
def mis_pedidos(request):
    pedidos = Pedido.objects.filter(
        cliente=request.user
    ).exclude(
        estado='entregado'
    ).order_by('-fecha_pedido')

    return render(request, 'core/mis_pedidos.html', {
        'pedidos': pedidos
    })


@login_required
def menusemanal(request):
    # 1) No permitir proveedores
    if hasattr(request.user, 'proveedor'):
        messages.error(request, "Los proveedores no tienen acceso al menú semanal.")
        return redirect('core:catalogo')

    # 2) Verificar si el usuario es cliente con convenio
    cliente = getattr(request.user, 'cliente', None)

    if not cliente:
        messages.error(request, "Este usuario no es un cliente válido.")
        return redirect('core:catalogo')

    if not cliente.empresa_convenio:
        messages.error(request, "Necesitas estar vinculado a una empresa convenio para usar el menú semanal.")
        return redirect('core:catalogo')

    # 3) Cargar o crear menú semanal
    menu, created = MenuSemanal.objects.get_or_create(cliente=cliente)

    # 4) Obtener todos los items del menú
    items = ItemMenu.objects.filter(menu=menu).select_related('plato')

    # 5) Estructurar los items en formato por día
    dias = {
        'lunes': None,
        'martes': None,
        'miercoles': None,
        'jueves': None,
        'viernes': None,
        'sabado': None,
        'domingo': None
    }

    for item in items:
        if item.dia_semana in dias:
            dias[item.dia_semana] = item

    # 6) Renderizar la plantilla del menú semanal
    return render(request, 'core/cliente/menusemanal.html', {
        'menu': menu,
        'dias': dias,
        'items': items,
        'cliente': cliente
    })
