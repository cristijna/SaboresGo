from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from .forms import UserRegisterForm, ProveedorProfileForm, LoginForm, PlatoForm, PedidoForm
from .models import Proveedor, Plato, Pedido, ItemMenu, MenuSemanal, Cliente
from django.contrib.auth.models import User
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import Plato, MenuSemanal, ItemMenu, Cliente


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
                Proveedor.objects.create(
                    user=user,
                    empresa=pform.cleaned_data.get('empresa'),
                    descripcion=pform.cleaned_data.get('descripcion'),
                    logo=pform.cleaned_data.get('logo')
                )
            else:
                # Crear perfil Cliente al registrarse como cliente
                Cliente.objects.create(user=user)

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

    # Detectar si viene desde menú semanal
    modo_menu = request.GET.get("modo_menu") == "true"
    dia = request.GET.get("dia")  # lunes, martes, etc.

    is_proveedor = False
    latest_pedido = None

    if request.user.is_authenticated:
        is_proveedor = hasattr(request.user, 'proveedor')

        if hasattr(request.user, 'cliente'):
            latest_pedido = (
                Pedido.objects
                .filter(cliente=request.user.cliente)
                .order_by('-creado_en')
                .first()
            )

    return render(request, 'core/catalogo.html', {
        'proveedores': proveedores,
        'is_proveedor': is_proveedor,
        'latest_pedido': latest_pedido,
        'modo_menu': modo_menu,
        'dia': dia
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
    # Pedidos del carrito del cliente actual (cliente es FK a Cliente)
    if not hasattr(request.user, 'cliente'):
        messages.error(request, "Necesitas una cuenta cliente para ver tus pedidos.")
        return redirect('core:catalogo')

    pedidos = Pedido.objects.filter(
        cliente=request.user.cliente,
        confirmado=False
    ).select_related('plato', 'plato__proveedor')

    # Confirmar todos los pedidos del carrito
    if request.method == 'POST' and 'confirmar_carrito' in request.POST:
        pedidos.update(confirmado=True, estado='pendiente')
        messages.success(request, 'Tu pedido fue confirmado. El restaurante comenzará la preparación.')
        return redirect('core:pedido_list')

    # Calcular total del carrito teniendo en cuenta cantidad
    total_carrito = sum(p.plato.precio * p.cantidad for p in pedidos)

    return render(request, 'core/cliente/pedido_list.html', {
        'pedidos': pedidos,
        'total_carrito': total_carrito
    })


@login_required
def pedido_create(request):
    if not hasattr(request.user, 'cliente'):
        messages.error(request, "Necesitas una cuenta cliente para crear pedidos.")
        return redirect('core:catalogo')

    if request.method == 'POST':
        form = PedidoForm(request.POST)
        if form.is_valid():
            pedido = form.save(commit=False)
            pedido.cliente = request.user.cliente
            pedido.save()
            messages.success(request, 'Pedido creado.')
            return redirect('core:pedido_list')
    else:
        form = PedidoForm()
    return render(request, 'core/cliente/pedido_form.html', {'form': form})


@login_required
def pedido_edit(request, pk):
    if not hasattr(request.user, 'cliente'):
        messages.error(request, "Necesitas una cuenta cliente para editar pedidos.")
        return redirect('core:catalogo')

    pedido = get_object_or_404(Pedido, pk=pk, cliente=request.user.cliente)
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
    if not hasattr(request.user, 'cliente'):
        messages.error(request, "Necesitas una cuenta cliente para eliminar pedidos.")
        return redirect('core:catalogo')

    pedido = get_object_or_404(Pedido, pk=pk, cliente=request.user.cliente)
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
    if not hasattr(request.user, 'cliente'):
        messages.error(request, "Necesitas una cuenta cliente para añadir al carrito.")
        return redirect('core:catalogo')

    plato = get_object_or_404(Plato, pk=pk)

    if request.method == 'POST':
        cantidad = int(request.POST.get('cantidad', 1))

        Pedido.objects.create(
            cliente=request.user.cliente,
            plato=plato,
            cantidad=cantidad,
            estado='pendiente',
            direccion="",
            confirmado=False
        )

        messages.success(request, 'Plato añadido al carrito.')
        return redirect('core:pedido_list')

    return redirect('core:plato_detalle', pk=pk)


@login_required
def pedido_detalle(request, pk):
    if not hasattr(request.user, 'cliente'):
        messages.error(request, "Necesitas una cuenta cliente para ver el detalle del pedido.")
        return redirect('core:catalogo')

    pedido = get_object_or_404(Pedido, pk=pk, cliente=request.user.cliente)
    return render(request, 'core/cliente/pedido_detalle.html', {'pedido': pedido})


@login_required
def mis_pedidos(request):
    if not hasattr(request.user, 'cliente'):
        messages.error(request, "Necesitas una cuenta cliente para ver tus pedidos.")
        return redirect('core:catalogo')

    pedidos = Pedido.objects.filter(
        cliente=request.user.cliente
    ).exclude(
        estado='entregado'
    ).order_by('-fecha_pedido')

    return render(request, 'core/mis_pedidos.html', {
        'pedidos': pedidos
    })


@login_required
def menu_semanal(request):
    if not hasattr(request.user, 'cliente'):
        messages.error(request, "Necesitas una cuenta cliente para usar esta función.")
        return redirect('core:catalogo')

    cliente = request.user.cliente

    DIAS = {
        'lunes': 'Lunes',
        'martes': 'Martes',
        'miercoles': 'Miércoles',
        'jueves': 'Jueves',
        'viernes': 'Viernes',
        'sabado': 'Sábado',
        'domingo': 'Domingo',
    }

    menu, _ = MenuSemanal.objects.get_or_create(cliente=cliente)
    items = {i.dia: i for i in menu.items.select_related('plato').all()}

    dias_lista = []
    for key, nombre in DIAS.items():
        dias_lista.append({
            "key": key,
            "nombre": nombre,
            "item": items.get(key),
        })

    return render(request, "core/cliente/menusemanal.html", {
        "dias": dias_lista,
    })




@login_required
def menu_semanal_select(request, dia):
    if not hasattr(request.user, 'cliente'):
        messages.error(request, "Usuario no válido.")
        return redirect('core:catalogo')

    cliente = request.user.cliente

    # Validación de día permitido
    DIAS_VALIDOS = ['lunes','martes','miercoles','jueves','viernes','sabado','domingo']

    if dia not in DIAS_VALIDOS:
        messages.error(request, "Día inválido.")
        return redirect('core:menu_semanal')

    # Cargar menú del cliente
    menu, _ = MenuSemanal.objects.get_or_create(cliente=cliente)

    # Obtener o crear item para el día
    item, _ = ItemMenu.objects.get_or_create(menu=menu, dia=dia)

    # Listar platos del proveedor del cliente
    platos = Plato.objects.all()


    if request.method == "POST":
        plato_id = request.POST.get("plato_id")
        item.plato_id = plato_id
        item.save()
        messages.success(request, "Plato asignado correctamente.")
        return redirect("core:menu_semanal")

    return render(request, "core/cliente/menusemanal_select.html", {
        "dia": dia,
        "item": item,
        "platos": platos,
    })


@login_required
def miperfil(request):
    return render(request, 'core/cliente/miperfil.html')