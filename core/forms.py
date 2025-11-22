from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import AuthenticationForm
from .models import Plato, Pedido, Proveedor

class UserRegisterForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput, label='Contraseña')
    password2 = forms.CharField(widget=forms.PasswordInput, label='Confirmar contraseña')

    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name']

    def clean(self):
        cleaned = super().clean()
        if cleaned.get('password') != cleaned.get('password2'):
            self.add_error('password2', 'Las contraseñas no coinciden.')
        return cleaned

class ProveedorProfileForm(forms.ModelForm):
    class Meta:
        model = Proveedor
        fields = ['empresa', 'descripcion', 'logo']

class PlatoForm(forms.ModelForm):
    class Meta:
        model = Plato
        fields = ['nombre', 'descripcion', 'precio', 'imagen']

class PedidoForm(forms.ModelForm):
    class Meta:
        model = Pedido
        fields = ['plato', 'cantidad', 'direccion']
        widgets = {
            'plato': forms.Select(),
        }

class LoginForm(AuthenticationForm):
    username = forms.CharField(label='Usuario')
    password = forms.CharField(widget=forms.PasswordInput, label='Contraseña')
