from django.db import models
from django.contrib.auth.models import User

class Proveedor(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    empresa = models.CharField(max_length=100, blank=True, null=True)
    descripcion = models.TextField(blank=True, null=True)
    telefono = models.CharField(max_length=20, blank=True, null=True)
    logo = models.ImageField(upload_to='logos/', blank=True, null=True)

    # 🔹 Campo requerido por el adminpanel:
    aprobado = models.BooleanField(default=False)

    def __str__(self):
        return self.empresa if self.empresa else self.user.username


class Ingrediente(models.Model):
    nombre = models.CharField(max_length=100)

    def __str__(self):
        return self.nombre
    
class Plato(models.Model):
    proveedor = models.ForeignKey(Proveedor, on_delete=models.CASCADE, related_name='platos')
    nombre = models.CharField(max_length=150)
    descripcion = models.TextField(blank=True)
    ingredientes = models.CharField(max_length=500)  # o TextField  # <-- CORPORATIVO
    precio = models.DecimalField(max_digits=8, decimal_places=2)
    imagen = models.ImageField(upload_to='platos/', blank=True, null=True)
    creado_en = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.nombre} - {self.proveedor.empresa}'


ESTADO_PEDIDO = (
    ('pendiente', 'Pendiente'),
    ('preparando', 'Preparando'),
    ('entregado', 'Entregado'),
)

class Pedido(models.Model):
    cliente = models.ForeignKey(User, on_delete=models.CASCADE, related_name='pedidos')
    plato = models.ForeignKey(Plato, on_delete=models.PROTECT, related_name='pedidos')
    cantidad = models.PositiveIntegerField(default=1)
    estado = models.CharField(max_length=20, choices=ESTADO_PEDIDO, default='pendiente')
    creado_en = models.DateTimeField(auto_now_add=True)
    direccion = models.CharField(max_length=255, blank=True)
    confirmado = models.BooleanField(default=False)
    fecha_pedido = models.DateTimeField(auto_now_add=True)


