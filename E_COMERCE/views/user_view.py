from django.views import View
from django.http import JsonResponse
from django.shortcuts import render
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth import get_user_model
import json

from E_COMERCE.services import user_service  # You’ll need to create this service module

User = get_user_model()


class UserListView(LoginRequiredMixin, View):
    login_url = 'admin_login'

    def get(self, request):
        users = user_service.get_all_users()
        return render(request, 'admin/user/user_list.html', {'users': users})


class UserCreateView(LoginRequiredMixin, View):
    login_url = 'admin_login'

    def get(self, request):
        return render(request, 'admin/user/user_create.html')

    def post(self, request):
        try:
            data = {
                'username':request.POST.get('email'),
                'email': request.POST.get('email'),
                'first_name': request.POST.get('first_name'),
                'last_name': request.POST.get('last_name'),
                'is_staff': request.POST.get('is_staff') == 'on',
                'is_admin': request.POST.get('is_admin') == 'on',
                'is_active': request.POST.get('is_active') == 'on',
                'password': request.POST.get('password')
            }
            user = user_service.create_user(data)
            return JsonResponse({'success': True, 'id': user.id})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})


class UserUpdateView(LoginRequiredMixin, View):
    login_url = 'admin_login'

    def get(self, request, user_id):
        user = user_service.get_user(user_id)
        return render(request, 'admin/user/user_update.html', {'user': user})

    def post(self, request, user_id):
        try:
            data = {
                'username': request.POST.get('username'),
                'email': request.POST.get('email'),
                'first_name': request.POST.get('first_name'),
                'last_name': request.POST.get('last_name'),
                'is_staff': request.POST.get('is_staff') == 'on',
                'is_active': request.POST.get('is_active') == 'on',
                'password': request.POST.get('password')
            }
            user_service.update_user(user_id, data)
            return JsonResponse({'success': True})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})



class ToggleUserStatusView(LoginRequiredMixin, View):
    login_url = 'admin_login'

    def post(self, request, user_id):
        try:
            data = json.loads(request.body)
            new_status = data.get('is_active')

            if new_status is None:
                return JsonResponse({'success': False, 'error': 'Missing is_active value'}, status=400)

            user = user_service.toggle_user_status(user_id, new_status)
            return JsonResponse({'success': True, 'new_status': user.is_active})

        except user_service.UserNotFoundError as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=404)

        except json.JSONDecodeError:
            return JsonResponse({'success': False, 'error': 'Invalid JSON'}, status=400)

        except Exception:
            return JsonResponse({'success': False, 'error': 'Something went wrong'}, status=500)
