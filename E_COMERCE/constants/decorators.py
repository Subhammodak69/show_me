from django.contrib.auth.mixins import AccessMixin
from django.shortcuts import redirect
from django.contrib.auth import logout
from E_COMERCE.constants.default_values import Role


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
