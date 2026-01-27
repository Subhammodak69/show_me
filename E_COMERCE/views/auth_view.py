from django.views import View
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout, get_user_model
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.utils import timezone
from django.conf import settings
import json
import random
import sendgrid
from sendgrid.helpers.mail import Mail
from datetime import timedelta

# Your imports (adjust paths)
from E_COMERCE.services import user_service
from E_COMERCE.constants.default_values import Role

User = get_user_model()
OTP_STORE = {}

def redirect_authenticated_user_to_home(view_func):
    def wrapper(request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('/')
        return view_func(request, *args, **kwargs)
    return wrapper

def send_otp_email(email, otp, subject="Your OTP Code"):
    """✅ SendGrid HTTP API - Works 100% on Render"""
    try:
        sg = sendgrid.SendGridAPIClient(api_key=settings.EMAIL_HOST_PASSWORD)
        
        message = Mail(
            from_email=settings.DEFAULT_FROM_EMAIL,
            to_emails=email,
            subject=subject,
            html_content=f"""<!DOCTYPE html>
            <html>
            <body style="font-family: Arial, sans-serif; margin: 0; padding: 20px;">
                <div style="max-width: 600px; margin: 0 auto;">
                    <h2 style="color: #333;">Your OTP Code</h2>
                    <div style="background: linear-gradient(135deg, #007bff, #0056b3); 
                               color: white; padding: 30px; text-align: center; 
                               font-size: 36px; font-weight: bold; border-radius: 12px;
                               box-shadow: 0 4px 15px rgba(0,123,255,0.3);">
                        {otp}
                    </div>
                    <p style="color: #666; margin: 20px 0; font-size: 16px;">
                        This code expires in 2-5 minutes.
                    </p>
                    <hr style="border: none; border-top: 1px solid #eee;">
                    <p style="color: #999; font-size: 14px;">
                        Do not share this code with anyone.
                    </p>
                </div>
            </body>
            </html>"""
        )
        response = sg.send(message)
        
        if response.status_code in (200, 202):
            print(f"✅ SENDGRID SUCCESS: OTP {otp} → {email} (Status: {response.status_code})")
            return True
        else:
            print(f"❌ SENDGRID FAILED: Status {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ SENDGRID ERROR: {e}")
        return False

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
                return JsonResponse({'success': False, 'message': 'Email and password required.'})

            if not user_service.user_exists(email):
                return JsonResponse({'success': False, 'message': 'Account not found.'})

            user = authenticate(request, username=email, password=password)
            if user:
                if hasattr(user, 'role') and user.role == Role.ENDUSER.value:
                    login(request, user)
                    return JsonResponse({'success': True, 'message': 'Login successful!', 'redirect': '/'})
                return JsonResponse({'success': False, 'message': 'Enduser access only.'})
            return JsonResponse({'success': False, 'message': 'Invalid credentials.'})
        except Exception as e:
            print(f"Login error: {e}")
            return JsonResponse({'success': False, 'message': 'Server error.'})

@method_decorator(csrf_exempt, name='dispatch')
@method_decorator(redirect_authenticated_user_to_home, name='dispatch')
class SigninView(View):
    def get(self, request):
        return render(request, 'auth/signin.html')

    def post(self, request):
        try:
            data = json.loads(request.body)
            email = data.get('email')
            first_name = data.get('first_name', '')
            last_name = data.get('last_name', '')
            password = data.get('password')
            otp_input = data.get('otp')

            # OTP Verification
            otp_record = OTP_STORE.get(email)
            if not otp_record:
                return JsonResponse({'success': False, 'message': 'OTP expired or not sent.'})

            if str(otp_input) != str(otp_record['otp']):
                return JsonResponse({'success': False, 'message': 'Invalid OTP.'})

            if timezone.now() > otp_record['expires_at']:
                del OTP_STORE[email]
                return JsonResponse({'success': False, 'message': 'OTP expired.'})

            # Create user
            if user_service.email_exists(email):
                del OTP_STORE[email]
                return JsonResponse({'success': False, 'message': 'Email exists. Please login.', 'redirect': '/login/'})

            user = User.objects.create_user(
                username=email,
                email=email,
                first_name=first_name,
                last_name=last_name,
                password=password
            )
            del OTP_STORE[email]
            return JsonResponse({'success': True, 'message': 'Registration successful! Login now.'})
        except Exception as e:
            print(f"Signin error: {e}")
            return JsonResponse({'success': False, 'message': 'Registration failed.'})

@method_decorator(csrf_exempt, name='dispatch')
class ForgetPasswordView(View):
    def get(self, request):
        return render(request, 'auth/forget_password.html')

    def post(self, request):
        try:
            data = json.loads(request.body)
            action = data.get('action')

            if action == 'send_otp':
                email = data.get('email')
                try:
                    User.objects.get(email=email)
                except User.DoesNotExist:
                    return JsonResponse({'success': False, 'message': 'Email not registered.'})

                otp = random.randint(100000, 999999)
                expires_at = timezone.now() + timedelta(minutes=5)
                OTP_STORE[email] = {'otp': otp, 'expires_at': expires_at}

                if send_otp_email(email, otp, "Password Reset OTP"):
                    return JsonResponse({'success': True, 'message': 'OTP sent! Check inbox/spam.'})
                else:
                    if email in OTP_STORE:
                        del OTP_STORE[email]
                    return JsonResponse({'success': False, 'message': 'Failed to send OTP.'})

            elif action == 'verify_otp':
                email = data.get('email')
                otp = data.get('otp')
                otp_record = OTP_STORE.get(email)

                if not otp_record:
                    return JsonResponse({'success': False, 'message': 'No OTP found.'})
                if timezone.now() > otp_record['expires_at']:
                    del OTP_STORE[email]
                    return JsonResponse({'success': False, 'message': 'OTP expired.'})
                if str(otp) != str(otp_record['otp']):
                    return JsonResponse({'success': False, 'message': 'Invalid OTP.'})

                return JsonResponse({'success': True, 'message': 'OTP verified! Set new password.'})

            elif action == 'set_password':
                email = data.get('email')
                otp = data.get('otp')
                new_password = data.get('new_password')

                otp_record = OTP_STORE.get(email)
                if (not otp_record or timezone.now() > otp_record['expires_at'] or 
                    str(otp) != str(otp_record['otp'])):
                    return JsonResponse({'success': False, 'message': 'Invalid/expired OTP.'})

                user = User.objects.get(email=email)
                user.set_password(new_password)
                user.save()
                del OTP_STORE[email]

                auth_user = authenticate(request, username=email, password=new_password)
                if auth_user:
                    login(request, auth_user)
                return JsonResponse({'success': True, 'message': 'Password reset! Logging in...', 'redirect': '/'})

            return JsonResponse({'success': False, 'message': 'Invalid action.'})
        except Exception as e:
            print(f"ForgetPassword error: {e}")
            return JsonResponse({'success': False, 'message': 'Server error.'})

@method_decorator(csrf_exempt, name='dispatch')
class SendOTPView(View):
    def post(self, request):
        try:
            data = json.loads(request.body)
            email = data.get('email')

            if not email:
                return JsonResponse({'success': False, 'message': 'Email required.'})

            user = user_service.email_user_exists(email)
            if user:
                if hasattr(user, 'role') and user.role == Role.ADMIN.value:
                    return JsonResponse({'success': False, 'message': 'Admin login → /admin/', 'redirect': '/admin/'})
                return JsonResponse({'success': False, 'message': 'Email exists. Login instead.', 'redirect': '/login/'})

            otp = random.randint(100000, 999999)
            expires_at = timezone.now() + timedelta(minutes=2)
            OTP_STORE[email] = {'otp': otp, 'expires_at': expires_at}

            if send_otp_email(email, otp, "Registration OTP"):
                return JsonResponse({'success': True, 'message': 'OTP sent! Check inbox/spam.'})
            else:
                if email in OTP_STORE:
                    del OTP_STORE[email]
                return JsonResponse({'success': False, 'message': 'Failed to send OTP.'})
        except Exception as e:
            print(f"SendOTP error: {e}")
            return JsonResponse({'success': False, 'message': 'Server error.'})


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
