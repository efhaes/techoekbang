from django.shortcuts import redirect
from django.contrib import messages
from functools import wraps


def desa_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')
        if not request.user.profile.is_desa():
            messages.error(request, "Akses ditolak.")
            return redirect('dashboard_kecamatan')
        return view_func(request, *args, **kwargs)
    return wrapper


def kecamatan_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')
        if not request.user.profile.is_kecamatan():
            messages.error(request, "Akses ditolak.")
            return redirect('dashboard_desa')
        return view_func(request, *args, **kwargs)
    return wrapper