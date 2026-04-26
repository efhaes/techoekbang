# ekbang/decorators.py
from django.core.exceptions import PermissionDenied
from functools import wraps


def desa_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not hasattr(request.user, 'profile'):
            raise PermissionDenied
        if not request.user.profile.is_desa():
            raise PermissionDenied
        return view_func(request, *args, **kwargs)
    return wrapper


def kecamatan_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not hasattr(request.user, 'profile'):
            raise PermissionDenied
        if not request.user.profile.is_kecamatan():
            raise PermissionDenied
        return view_func(request, *args, **kwargs)
    return wrapper