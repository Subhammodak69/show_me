# show_me
=>This is a E-commerce web application 

# git clone:
=> git clone https://github.com/Subhammodak69/show_me.git

# open and go to vscode:
=> cd show_me
    code .

# Made venv:
=> python -m venv venv

# Activate Scripts of venv:
=> .\venv\Scripts\Activate

# Install all requirements:
=> pip install -r requirements.txt

# Migration:
=>python manage.py makemigrations E_COMERCE
    =>python manage.py migrate

# Runserver:
=> python manage.py runserver

# For Data Recover into Local postgresql:
=> Uncomment This code:

    # This is for local db to cloud db transaction
     DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': 'show_me_db',
            'USER': 'postgres',
            'PASSWORD': '2025',
            'HOST': 'localhost',
            'PORT': '5432',
        },
        'local': { 
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': env('DB_NAME'),
            'USER': env('DB_USER'),
            'PASSWORD': env('DB_PASSWORD'),
            'HOST': env('DB_HOST', default='localhost'),
            'PORT': env('DB_PORT', default='5432'),
            'OPTIONS': {
                'sslmode': 'require' if not DEBUG else 'prefer',
            },
        }
    }

    # This is for cloud db to local db transaction
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': env('DB_NAME'),
            'USER': env('DB_USER'),
            'PASSWORD': env('DB_PASSWORD'),
            'HOST': env('DB_HOST', default='localhost'),
            'PORT': env('DB_PORT', default='5432'),
            'OPTIONS': {
                'sslmode': 'require' if not DEBUG else 'prefer',
            },
        },
        'local': { 
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': 'show_me_db',
            'USER': 'postgres',
            'PASSWORD': '2025',
            'HOST': 'localhost',
            'PORT': '5432',
        }
    }


=> Then run this command in terminal:
    python manage.py sync_all --dry-run 
    python manage.py sync_all
