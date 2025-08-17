from django.apps import AppConfig
from django.db.models.signals import post_migrate
from django.contrib.auth import get_user_model

class EComerceConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'E_COMERCE'

    def ready(self):
        def create_admin(sender, **kwargs):
            User = get_user_model()
            if not User.objects.filter(username='admin').exists():
                User.objects.create_superuser(
                    username='admin',
                    email='modaksubham69@gmail.com',
                    password='123456',
                    role=2 
                )

        post_migrate.connect(create_admin)
