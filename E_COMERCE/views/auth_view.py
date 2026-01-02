from django.views import View
from django.shortcuts import render,redirect
from django.contrib.auth import authenticate,login,logout,get_user_model
from django.contrib.auth.hashers import make_password
import random
from show_me.settings import EMAIL_HOST_USER
from django.core.mail import send_mail
from E_COMERCE.models import User
from django.http import JsonResponse
from django.utils import timezone
import json
from E_COMERCE.services import user_service
from E_COMERCE.constants.default_values import Role
from E_COMERCE.constants.decorators import redirect_authenticated_user_to_home
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt

# Temporary OTP storage (or use session/cache/DB)
OTP_STORE = {}

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
        data = json.loads(request.body)
        email = data.get('email')
        first_name = data.get('first_name')
        last_name = data.get('last_name')
        password = data.get('password')
        otp_input = data.get('otp')

        # 1. OTP Verification
        otp_record = OTP_STORE.get(email)
        if not otp_record:
            return JsonResponse({'success': False, 'message': 'OTP expired or not sent.'})
        
        if str(otp_input) != str(otp_record['otp']):
            return JsonResponse({'success': False, 'message': 'Invalid OTP.'})

        # 2. OTP expiry check
        if timezone.now() > otp_record['expires_at']:
            return JsonResponse({'success': False, 'message': 'OTP expired.'})

        # 3. Create user
        user_exists = user_service.email_exists(email)
        if user_exists:
            return JsonResponse({'success': False, 'message': 'User already exists. Please login. Redirecting..........'})

        user = User.objects.create_user(
            username=email,
            email=email,
            first_name=first_name,
            last_name=last_name,
            password=password
        )
        del OTP_STORE[email]  # clear OTP
        return JsonResponse({'success': True, 'message': 'Registration successful! You can now login.'})




User = get_user_model()
@method_decorator(csrf_exempt, name='dispatch')
class ForgetPasswordView(View):
    def get(self, request):
        return render(request, 'auth/forget_password.html')

    def post(self, request):
        data = json.loads(request.body)
        action = data.get('action')

        if action == 'send_otp':
            email = data.get('email')

            try:
                user = User.objects.get(email=email)
            except User.DoesNotExist:
                return JsonResponse({'success': False, 'message': 'Email not registered.'})

            otp = random.randint(100000, 999999)
            print(otp)
            expires_at = timezone.now() + timedelta(minutes=5)

            OTP_STORE[email] = {'otp': otp, 'expires_at': expires_at}

            subject = 'Your Password Reset OTP'
            message = f'Your OTP to reset password is: {otp}. It is valid for 5 minutes.'
            from_email = EMAIL_HOST_USER

            try:
                send_mail(subject, message, from_email, [email])
                return JsonResponse({'success': True, 'message': 'OTP sent to your email.'})
            except Exception as e:
                return JsonResponse({'success': False, 'message': 'Failed to send OTP email.'})

        elif action == 'verify_otp':
            email = data.get('email')
            otp = data.get('otp')

            otp_record = OTP_STORE.get(email)
            if not otp_record:
                return JsonResponse({'success': False, 'message': 'No OTP requested for this email.'})

            if timezone.now() > otp_record['expires_at']:
                del OTP_STORE[email]
                return JsonResponse({'success': False, 'message': 'OTP expired. Please request again.'})

            if str(otp) != str(otp_record['otp']):
                return JsonResponse({'success': False, 'message': 'Invalid OTP.'})

            return JsonResponse({'success': True, 'message': 'OTP verified. You can reset your password.'})

        elif action == 'set_password':
            email = data.get('email')
            otp = data.get('otp')
            new_password = data.get('new_password')

            otp_record = OTP_STORE.get(email)
            if not otp_record or timezone.now() > otp_record['expires_at'] or str(otp) != str(otp_record['otp']):
                return JsonResponse({'success': False, 'message': 'Invalid or expired OTP.'})

            try:
                user = User.objects.get(email=email)
                user.password = make_password(new_password)
                user.save()
                del OTP_STORE[email]

                # Authenticate and login user automatically after password reset
                auth_user = authenticate(request, username=user.username, password=new_password)
                if auth_user:
                    login(request, auth_user)
                return JsonResponse({'success': True, 'message': 'Password reset successful. redirecting...........'})
            except User.DoesNotExist:
                return JsonResponse({'success': False, 'message': 'User not found.'})

        else:
            return JsonResponse({'success': False, 'message': 'Invalid action.'})


@method_decorator(csrf_exempt, name='dispatch')
class SendOTPView(View):
    def post(self, request):
        data = json.loads(request.body)
        email = data.get('email')
        user = user_service.email_user_exists(email)
        print(user)
        if user:
            if user.role == Role.ADMIN.value and user.email == email:
                return JsonResponse({
                    'success': False,
                    'message': 'Email already exists as Admin. Redirecting........',
                    'redirect': '/admin/'
                })
            return JsonResponse({
                'success': False,
                'message': 'Email already exists. Redirecting........',
                'redirect': '/login/'
            })

        otp = random.randint(100000, 999999)
        expires_at = timezone.now() + timezone.timedelta(minutes=2)

        OTP_STORE[email] = {'otp': otp, 'expires_at': expires_at}
        print("otp:", otp)

        subject = 'Your OTP Code'
        message = f'Your One-Time Password (OTP) is: {otp}'
        from_email = EMAIL_HOST_USER

        try:
            send_mail(subject, message, from_email, [email])
            return JsonResponse({'success': True, 'message': 'OTP sent to your email.'})
        except Exception as e:
            print("Error sending email:", e)
            return JsonResponse({'success': False, 'message': 'Failed to send OTP.'})

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
        # print("email=>",email,"password=>",password)
        user = user_service.user_is_authenticate(email)
        # print("user:",user)

        if user and user.role == Role.ADMIN.value:
            login(request, user) 
            return redirect('admin')
        else:
            print("elseeeee")
            return render(request, 'admin/admin_login.html', {
                'error': 'Invalid credentials or not an admin user.'
            })
        
from django.http import JsonResponse
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
