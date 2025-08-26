from django.contrib.auth.mixins import AccessMixin
from django.shortcuts import redirect
from django.contrib.auth import logout
from E_COMERCE.constants.default_values import Role
from functools import wraps


class AdminRequiredMixin(AccessMixin):
    login_url = '/admin-login/'

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()

        if getattr(request.user, 'role', None) != Role.ADMIN.value:
            logout(request)
            return redirect(self.login_url)

        return super().dispatch(request, *args, **kwargs)


class EnduserRequiredMixin(AccessMixin):
    login_url = '/login/'

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()

        if getattr(request.user, 'role', None) != Role.ENDUSER.value:
            logout(request)
            return redirect(self.login_url)

        return super().dispatch(request, *args, **kwargs)


def redirect_authenticated_user_to_home(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('home')  # replace 'home' with your home page URL name
        return view_func(request, *args, **kwargs)
    return _wrapped_view