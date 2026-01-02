from E_COMERCE.models import User
from django.contrib.auth import get_user_model
User = get_user_model()
from E_COMERCE.constants.default_values import Role


def email_exists(email):
    return User.objects.filter(email=email).exists()

def email_user_exists(email):
    return User.objects.filter(email=email).first()

def user_exists(email):
    return User.objects.filter(email = email , role= Role.ENDUSER.value).exists()


def user_is_authenticate(email):
    try:
        user = User.objects.get(email=email)
        return user
    except User.DoesNotExist:
        return None  
    


class UserNotFoundError(Exception):
    pass


def get_all_users():
    return User.objects.all().order_by('id')


def create_user(data):
    username = data.get('username') or data['email'].split('@')[0]

    user = User.objects.create_user(
        username=username,
        email=data['email'],
        first_name=data.get('first_name', ''),
        last_name=data.get('last_name', ''),
        is_staff=data.get('is_staff', False),
        role= Role.ADMIN.value if data.get('is_admin') == True else Role.ENDUSER.value ,
        is_active=data.get('is_active', True),
        password=data['password']
    )
    return user



def get_user(user_id):
    try:
        return User.objects.get(id=user_id)
    except User.DoesNotExist:
        raise UserNotFoundError("User not found")


def update_user(user_id, data):
    user = get_user(user_id)
    user.email = data.get('email', user.email)
    user.first_name = data.get('first_name', user.first_name)
    user.last_name = data.get('last_name', user.last_name)
    user.is_staff = data.get('is_staff', user.is_staff)
    user.is_active = data.get('is_active', user.is_active)
    if 'password' in data and data['password']:
        user.set_password(data['password'])
    user.save()
    return user


def toggle_user_status(user_id, new_status):
    user = get_user(user_id)
    user.is_active = new_status
    user.save()
    return user


def get_all_user():
    return User.objects.all()

def get_total_user_count():
    return User.objects.count()