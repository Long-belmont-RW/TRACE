from django.core.exceptions import PermissionDenied
from django.contrib.auth.mixins import AccessMixin
from functools import wraps

def role_required(*allowed_roles):
    """
    Decorator for views that checks that the user is logged in and has a permitted role.
    Raises PermissionDenied (HTTP 403) if the user fails the role check.
    """
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if not request.user.is_authenticated:
                from django.contrib.auth.views import redirect_to_login
                return redirect_to_login(request.get_full_path())
            if request.user.role not in allowed_roles and not ('SUPERADMIN' in allowed_roles and getattr(request.user, 'is_superuser', False)):
                raise PermissionDenied("You do not have permission to access this resource.")
            return view_func(request, *args, **kwargs)
        return _wrapped_view
    return decorator

class RoleRequiredMixin(AccessMixin):
    """
    Verify that the current user is authenticated and has an allowed role.
    """
    allowed_roles = []

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()
        if request.user.role not in self.allowed_roles and not ('SUPERADMIN' in self.allowed_roles and getattr(request.user, 'is_superuser', False)):
            raise PermissionDenied("You do not have permission to access this resource.")
        return super().dispatch(request, *args, **kwargs)
