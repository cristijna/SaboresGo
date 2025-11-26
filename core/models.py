from django.db import models
from django.contrib.auth.models import User


# ---------------------------------------------------------
# PROVEEDOR (SIN CAMBIOS)
# ---------------------------------------------------------
class Proveedor(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    empresa = models.CharField(max_length=100, blank=True, null=True)
    descripcion = models.TextField(blank=True, null=True)
    telefono = models.CharField(max_length=20, blank=True, null=True)
    logo = models.ImageField(upload_to='logos/', blank=True, null=True)

    aprobado = models.BooleanField(default=False)

    def __str__(self):
        return self.empresa if self.empresa else self.user.username



# ---------------------------------------------------------
# MODELOS BASE (SIN CAMBIOS)
# ---------------------------------------------------------
class Ingrediente(models.Model):
    nombre = models.CharField(max_length=100)

    def __str__(self):
        return self.nombre


class Plato(models.Model):
    proveedor = models.ForeignKey(Proveedor, on_delete=models.CASCADE, related_name='platos')
    nombre = models.CharField(max_length=150)
    descripcion = models.TextField(blank=True)
    ingredientes = models.CharField(max_length=500)
    precio = models.DecimalField(max_digits=8, decimal_places=2)
    imagen = models.ImageField(upload_to='platos/', blank=True, null=True)
    creado_en = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.nombre} - {self.proveedor.empresa}'



# ---------------------------------------------------------
# EMPRESA CONVENIO
# ---------------------------------------------------------
class EmpresaConvenio(models.Model):
    nombre = models.CharField(max_length=100, unique=True)
    saldo_mensual = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return self.nombre



# ---------------------------------------------------------
# CODIGO CONVENIO (SIN INDICADOR DE “USADO”)
# ---------------------------------------------------------
class CodigoConvenio(models.Model):
    empresa = models.ForeignKey(EmpresaConvenio, on_delete=models.CASCADE, related_name='codigos')
    codigo = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return f'{self.codigo} - {self.empresa.nombre}'



# ---------------------------------------------------------
# CLIENTE
# ---------------------------------------------------------
class Cliente(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    direccion = models.CharField(max_length=255, blank=True)

    empresa = models.ForeignKey(
        EmpresaConvenio,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='clientes'
    )

    saldo = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    def __str__(self):
        return self.user.username



# ---------------------------------------------------------
# PEDIDO → AHORA USA CLIENTE, NO USER
# ---------------------------------------------------------
ESTADO_PEDIDO = (
    ('pendiente', 'Pendiente'),
    ('preparando', 'Preparando'),
    ('listo', 'Listo'),
    ('entregado', 'Entregado'),
)

class Pedido(models.Model):
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE, related_name='pedidos')
    plato = models.ForeignKey(Plato, on_delete=models.PROTECT, related_name='pedidos')
    cantidad = models.PositiveIntegerField(default=1)
    estado = models.CharField(max_length=20, choices=ESTADO_PEDIDO, default='pendiente')
    creado_en = models.DateTimeField(auto_now_add=True)
    direccion = models.CharField(max_length=255, blank=True)
    confirmado = models.BooleanField(default=False)
    fecha_pedido = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Pedido {self.id} - {self.cliente.user.username}'



# ---------------------------------------------------------
# MENU SEMANAL
# ---------------------------------------------------------
class MenuSemanal(models.Model):
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE, related_name='menus_semanales')
    total = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    pagado = models.BooleanField(default=False)
    creado_en = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Menu Semanal #{self.id} - {self.cliente.user.username}'



# ---------------------------------------------------------
# ITEM DEL MENU SEMANAL
# ---------------------------------------------------------
DIAS_SEMANA = [
    ('lunes', 'Lunes'),
    ('martes', 'Martes'),
    ('miercoles', 'Miércoles'),
    ('jueves', 'Jueves'),
    ('viernes', 'Viernes'),
    ('sabado', 'Sábado'),
    ('domingo', 'Domingo'),
]

class ItemMenu(models.Model):
    menu = models.ForeignKey(MenuSemanal, on_delete=models.CASCADE, related_name='items')
    plato = models.ForeignKey(Plato, on_delete=models.SET_NULL, null=True, blank=True)
    dia = models.CharField(max_length=20, choices=DIAS_SEMANA)
    hora_colacion = models.TimeField(null=True, blank=True)
    cantidad = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f'{self.dia} - {self.plato}'
