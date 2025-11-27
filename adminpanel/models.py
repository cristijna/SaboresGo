from django.db import models
from django.contrib.auth.models import User


class EmpresaConvenio(models.Model):
    """
    Empresa creada por el administrador.
    Cada empresa tiene:
    - nombre
    - código único que el cliente ingresa en Mi Perfil
    - saldo mensual individual que recibe cada trabajador asociado
    """
    nombre = models.CharField(max_length=150)
    codigo = models.CharField(max_length=30, unique=True)
    saldo_mensual = models.DecimalField(max_digits=10, decimal_places=2)

    activo = models.BooleanField(default=True)

    creado_en = models.DateTimeField(auto_now_add=True)
    actualizado_en = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.nombre} ({self.codigo})"


class Cliente(models.Model):
    """
    Perfil del usuario tipo Cliente.
    NO guarda nada en User, solo se conecta con él.
    Guarda:
    - dirección
    - empresa de convenio (opcional)
    - si el convenio está activo
    - saldo disponible PERSONAL
    """
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='cliente_adminpanel'
    )

    direccion = models.CharField(
        max_length=255,
        blank=True,
        null=True
    )

    empresa = models.ForeignKey(
        EmpresaConvenio,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='clientes'
    )

    convenio_activo = models.BooleanField(default=False)

    saldo_disponible = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0
    )

    creado_en = models.DateTimeField(auto_now_add=True)
    actualizado_en = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Cliente: {self.user.username}"


class Repartidor(models.Model):
    """
    Repartidor visible para cualquiera en la vista global.
    Puede o no estar ligado a un User.
    """
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='repartidor',
        blank=True,
        null=True
    )

    nombre = models.CharField(max_length=150)
    telefono = models.CharField(max_length=30, blank=True, null=True)
    zona_reparto = models.CharField(max_length=150, blank=True, null=True)

    activo = models.BooleanField(default=True)

    creado_en = models.DateTimeField(auto_now_add=True)
    actualizado_en = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.nombre
