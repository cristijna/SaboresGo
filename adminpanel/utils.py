from django.shortcuts import redirect
from django.contrib import messages

def admin_required(view_func):
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated or not request.user.is_staff:
            messages.error(request, "Acceso restringido a administradores.")
            return redirect('core:catalogo')
        return view_func(request, *args, **kwargs)
    return _wrapped_view
