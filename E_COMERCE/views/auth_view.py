from django.shortcuts import redirect,render
from django.http import JsonResponse
import json
from django.views import View
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import authenticate, login, logout, get_user_model
from E_COMERCE.services import user_service
from E_COMERCE.constants.default_values import Role
from django.shortcuts import render, redirect


User = get_user_model()


def redirect_authenticated_user_to_home(view_func):
    """Redirect authenticated users away from auth pages"""
    def wrapper(request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('/')
        return view_func(request, *args, **kwargs)
    return wrapper


@method_decorator(redirect_authenticated_user_to_home, name='dispatch')
@method_decorator(csrf_exempt, name='dispatch')
class LoginView(View):
    def get(self, request):
        return render(request, 'auth/login.html')

    def post(self, request):
        try:
            data = json.loads(request.body)
            email = data.get('email')
            password = data.get('password')

            if not email or not password:
                return JsonResponse({'success': False, 'message': 'Email and password are required.'})

            if not user_service.user_exists(email):
                return JsonResponse({'success': False, 'message': 'Account not found with this email.'})

            user = authenticate(request, username=email, password=password)
            if user:
                if user.role == Role.ENDUSER.value:
                    login(request, user)
                    return JsonResponse({'success': True, 'message': 'Login successful! Redirecting...'})
                else:
                    return JsonResponse({'success': False, 'message': 'You are not an enduser.'})
            else:
                return JsonResponse({'success': False, 'message': 'Incorrect password.'})
        except Exception as e:
            return JsonResponse({'success': False, 'message': 'Something went wrong. Please try again.'})


@method_decorator(csrf_exempt, name='dispatch')
@method_decorator(redirect_authenticated_user_to_home, name='dispatch')
class SigninView(View):
    def get(self, request):
        return render(request, 'auth/signin.html')

    def post(self, request):
        try:
            data = json.loads(request.body)
            email = data.get('email')
            first_name = data.get('first_name', '').strip()
            last_name = data.get('last_name', '').strip()
            password = data.get('password')

            if not all([email, password]):
                return JsonResponse({'success': False, 'message': 'Email and password are required.'})

            # Check if user already exists
            user_exists = user_service.email_exists(email)
            if user_exists:
                return JsonResponse({
                    'success': False, 
                    'message': 'User already exists. Please login instead.', 
                    'redirect': '/login/'
                })

            # Create user directly
            user = User.objects.create_user(
                username=email,
                email=email,
                first_name=first_name,
                last_name=last_name,
                password=password
            )
            user.role = Role.ENDUSER.value
            user.save()

            # Auto-login after signup
            auth_user = authenticate(request, username=email, password=password)
            if auth_user:
                login(request, auth_user)

            return JsonResponse({
                'success': True, 
                'message': 'Registration successful! Logging you in...', 
                'redirect': '/'
            })

        except Exception as e:
            return JsonResponse({'success': False, 'message': 'Registration failed. Please try again.'})


@method_decorator(csrf_exempt, name='dispatch')
class ForgetPasswordView(View):
    def get(self, request):
        return render(request, 'auth/forget_password.html')

    def post(self, request):
        try:
            data = json.loads(request.body)
            action = data.get('action')

            if action == 'reset_password':
                email = data.get('email')
                new_password = data.get('new_password')

                if not all([email, new_password]):
                    return JsonResponse({'success': False, 'message': 'Email and new password are required.'})

                try:
                    user = User.objects.get(email=email)
                except User.DoesNotExist:
                    return JsonResponse({'success': False, 'message': 'Email not registered.'})

                # Set new password directly
                user.set_password(new_password)
                user.save()

                # Auto-login after password reset
                auth_user = authenticate(request, username=email, password=new_password)
                if auth_user:
                    login(request, auth_user)

                return JsonResponse({
                    'success': True, 
                    'message': 'Password reset successful! Logging you in...', 
                    'redirect': '/'
                })

            else:
                return JsonResponse({'success': False, 'message': 'Invalid action.'})

        except Exception as e:
            return JsonResponse({'success': False, 'message': 'Something went wrong. Please try again.'})


@method_decorator(csrf_exempt, name='dispatch')    
class LogoutView(View):
    def post(self, request):
        if request.user.role == Role.ENDUSER.value:
            logout(request)
            return redirect('/login/')  
        logout(request)
        return redirect('/admin-login/')
    
    
    
#admin Authentication
@method_decorator(csrf_exempt, name='dispatch')
class AdminLoginView(View):
    def get(self, request):
        return render(request, 'admin/admin_login.html')

    def post(self, request):
        email = request.POST.get('email')
        password = request.POST.get('password')
        try:
            user = User.objects.get(email=email, is_active=True)
            if user.check_password(password):
                if(user.role == Role.ADMIN.value or user.is_superuser):
                    login(request, user)
                    return redirect('admin')
                else:
                    return render(request, 'admin/admin_login.html', {
                        'error': 'User not an admin.'
                    })
            else:
                return render(request, 'admin/admin_login.html', {
                    'error': 'Invalid credentials.'
                })
        except User.DoesNotExist:
            return render(request, 'admin/admin_login.html', {
                'error': 'User does not exist.'
            })




        

from django.utils.timezone import now
from datetime import timedelta
from django.db.models.functions import TruncDay
from django.db.models import Count

from E_COMERCE.models import Order  # adjust if your model path is different

def sales_chart_data(request):
    today = now().date()
    last_7_days = today - timedelta(days=6)

    orders = (
        Order.objects
        .filter(created_at__date__gte=last_7_days)
        .annotate(day=TruncDay('created_at'))
        .values('day')
        .annotate(count=Count('id'))
        .order_by('day')
    )

    labels = [o['day'].strftime('%a') for o in orders]
    data = [o['count'] for o in orders]

    return JsonResponse({'labels': labels, 'data': data})



def visiting_users_data(request):
    today = now().date()
    last_7_days = today - timedelta(days=6)
    
    visits = (
        User.objects.filter(created_at__date__gte=last_7_days)
        .annotate(day=TruncDay('created_at'))
        .values('day')
        .annotate(count=Count('id'))
        .order_by('day')
    )

    labels = [v['day'].strftime('%b %d') for v in visits]
    data = [v['count'] for v in visits]

    return JsonResponse({'labels': labels, 'data': data})
