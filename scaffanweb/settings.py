"""
Django settings for scaffanweb project.

Generated by 'django-admin startproject' using Django 3.0.3.

For more information on this file, see
https://docs.djangoproject.com/en/3.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/3.0/ref/settings/
"""

import os

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
from pathlib import Path
scpath = Path(__file__).parent / "secretkey.txt"
if scpath.exists():
    with open(scpath, "r") as f:
        SECRET_KEY = f.read().strip()
else:
    with open(scpath, "w") as f:
        from django.core.management.utils import get_random_secret_key
        SECRET_KEY = f.write(
            get_random_secret_key()
        )
# from . import secrets
# SECRET_KEY = secrets.SECRET_KEY

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = [
    # "0.0.0.0:8000",
    "147.228.47.162",
    "127.0.0.1",
    "scaffan.kky.zcu.cz",
    # "*",
]

SITE_ID = 2 # because in my database is in table Sites my 127.0.0.1 on second place
LOGIN_REDIRECT_URL = '/'


# Application definition

INSTALLED_APPS = [
    "microimprocessing.apps.DataimportConfig",
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',
    # 'social_app',  # <--
    'allauth',  # <--
    'allauth.account',  # <--
    'allauth.socialaccount',  # <--
    'allauth.socialaccount.providers.google',  # <--
    'django_q',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'scaffanweb.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'scaffanweb.wsgi.application'

if os.name == "nt":
    # windows
    CONDA_EXECUTABLE=r"C:\Users\Jirik\Miniconda3\Scripts\conda.exe"
# elif os.name == "posix": #linux
else:
    CONDA_EXECUTABLE="/home/mjirik/miniconda/condabin/conda"


# Database
# https://docs.djangoproject.com/en/3.0/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}


# Password validation
# https://docs.djangoproject.com/en/3.0/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/3.0/topics/i18n/

LANGUAGE_CODE = 'en-us'

# TIME_ZONE = 'UTC'
TIME_ZONE = 'Europe/Prague'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.0/howto/static-files/

# STATIC_URL = '/static/'
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
STATIC_URL = '/static/'
# use python manage.py collectstatic
STATIC_ROOT = os.path.join(BASE_DIR, "static")
# STATIC_ROOT = "static"
# STATICFILES_DIRS = (
#     os.path.join(BASE_DIR, "static"),
# )


AUTHENTICATION_BACKENDS = (
 'django.contrib.auth.backends.ModelBackend',
 'allauth.account.auth_backends.AuthenticationBackend',
 )

SOCIALACCOUNT_PROVIDERS = {
    'google': {
        'SCOPE': [
            'profile',
            'email',
        ],
        'AUTH_PARAMS': {
            'access_type': 'online',
        }
    }
}

# Q_CLUSTER = {
#     'name': 'DjangoORM',
#     'timeout': 1200,	# Timeout in secs for a task
#     'save_limit': 10,	# Store latest 10 results only
#     'catch_up': False,	# Ignore un-run scheduled tasks
#     'orm': 'default'	# Django database connection
# }
# # In django_demo/settings.py
# CACHES = {
#     'default': {
# 		'BACKEND': \
# 			'django.core.cache.backends.locmem.LocMemCache',
#         'LOCATION': 'djangoq-localmem',
#     }
# }
# Q_CLUSTER = {'orm': 'default', 'sync': True}

# Q_CLUSTER = {
#     'name': 'myproject',
#     'workers': 8,
#     'recycle': 500,
#     'timeout': 60,
#     'compress': True,
#     'cpu_affinity': 1,
#     'save_limit': 250,
#     'queue_limit': 500,
#     'label': 'Django Q',
#     'redis': {
#         'host': '127.0.0.1',
#         'port': 6379,
#         'db': 0, }
# }


Q_CLUSTER = {
    'name': 'foo',
    'workers': 1,
    'cpu_affinity': 1,
    'sync': True,
    'timeout': 60,
    'catch_up': True,
    'recycle': 20,
    'compress': False,
    'save_limit': 250,
    'queue_limit': 500,
    'label': 'Django Q',
    'orm': 'default',
}