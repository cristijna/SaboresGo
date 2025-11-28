from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import AuthenticationForm
from .models import Plato, Pedido, Proveedor

class UserRegisterForm(forms.ModelForm):
    password = forms.CharField(
        widget=forms.PasswordInput,
        label='Contraseña',
        help_text="Debe contener al menos 8 caracteres, una mayúscula, una minúscula, un número y un símbolo."
    )
    password2 = forms.CharField(
        widget=forms.PasswordInput,
        label='Confirmar contraseña'
    )

    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name']

    def clean_password(self):
        pwd = self.cleaned_data.get("password")

        import re

        errores = []

        if len(pwd) < 8:
            errores.append("Debe tener al menos 8 caracteres.")

        if not re.search(r"[A-Z]", pwd):
            errores.append("Debe contener al menos una letra mayúscula.")

        if not re.search(r"[a-z]", pwd):
            errores.append("Debe contener al menos una letra minúscula.")

        if not re.search(r"[0-9]", pwd):
            errores.append("Debe contener al menos un número.")

        if not re.search(r"[!@#$%^&*()_+\-=\[\]{};':\"\\|,.<>/?]", pwd):
            errores.append("Debe contener al menos un caracter especial.")

        if errores:
            raise forms.ValidationError(errores)

        return pwd

    def clean(self):
        cleaned = super().clean()
        pwd = cleaned.get("password")
        pwd2 = cleaned.get("password2")

        if pwd and pwd2 and pwd != pwd2:
            self.add_error("password2", "Las contraseñas no coinciden.")

        return cleaned


class ProveedorProfileForm(forms.ModelForm):
    class Meta:
        model = Proveedor
        fields = ['empresa', 'descripcion', 'logo']

class PlatoForm(forms.ModelForm):
    ingredientes = forms.CharField(
        widget=forms.Textarea(
            attrs={
                'rows': 3,
                'placeholder': 'Ingrese los ingredientes separado por coma.',
                'class': 'form-control'
            }
        ),
        help_text="Ingrese los ingredientes separados por coma."
    )

    class Meta:
        model = Plato
        fields = ['nombre', 'descripcion', 'ingredientes', 'precio', 'imagen']

    def clean_ingredientes(self):
        data = self.cleaned_data['ingredientes']
        # Limpieza corporativa: estandarizar formato
        return ", ".join([i.strip() for i in data.split(",") if i.strip()])



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
