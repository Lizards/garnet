"""
Django settings for djangobot project.

Generated by 'django-admin startproject' using Django 2.1.1.

For more information on this file, see
https://docs.djangoproject.com/en/2.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/2.1/ref/settings/
"""

import os
import sys

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
APP_NAME = 'djangobot'
TIER = os.environ.get('TIER', 'dev')
DEBUG = False
SESSION_COOKIE_NAME = f'{APP_NAME}_session'
LOG_LEVEL = os.environ.get('LOG_LEVEL', 'INFO')
LOGGING_HANDLERS = ['console']

try:
    LOCAL_ALLOWED_HOSTS = os.environ.get('LOCAL_ALLOWED_HOSTS').split(',')
except AttributeError as e:
    LOCAL_ALLOWED_HOSTS = []

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/2.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'vgq+9#rky+0&3h(#bz)47w=(sm%g6ng!0ujzo4%@=bzfie+y5h'

# Database settings
if 'py.test' in sys.argv[0] or 'collectstatic' in sys.argv:
    DB_ENGINE = 'django.db.backends.sqlite3'
    DB_NAME = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), '/test.db')
    DB_PORT = ''
    DB_HOST = ''
    DB_USER = ''
    DB_PASSWORD = ''
else:
    DB_ENGINE = 'django.db.backends.mysql'
    DB_PORT = 3306
    DB_HOST = os.environ.get('DB_HOST', 'djangobot.db.example.com')
    DB_NAME = os.environ.get('DB_NAME', 'garnet')
    DB_USER = os.environ.get('DB_USER', 'garnet')
    try:
        DB_PASSWORD = os.environ['DB_PASSWORD']
    except KeyError as e:
        print("*** Unable to fetch password from environment variable DB_PASSWORD; if in development, please define in local_settings.py")

CACHE_HOST = os.environ.get('CACHE_HOST')
CACHE_PORT = os.environ.get('CACHE_PORT', 11211)

try:
    from djangobot.local_settings import *
except ImportError as e: # pragma: nocover
    if TIER == 'local':
        print(f'Issue importing local_settings.py: {e}')

ALLOWED_HOSTS = [ '127.0.0.1', 'localhost', '0.0.0.0' ] + LOCAL_ALLOWED_HOSTS
TEMPLATE_DEBUG = DEBUG


# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'djangobot',
    'personality',
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

ROOT_URLCONF = 'djangobot.urls'

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

WSGI_APPLICATION = 'djangobot.wsgi.application'


# Database
# https://docs.djangoproject.com/en/2.1/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': DB_ENGINE,
        'NAME': DB_NAME,
        'USER': DB_USER,
        'PASSWORD': DB_PASSWORD,
        'HOST': DB_HOST,
        'PORT': DB_PORT,
    }
}

# Cache
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.memcached.MemcachedCache',
        'LOCATION': f'{CACHE_HOST}:{CACHE_PORT}',
    }
}

# Password validation
# https://docs.djangoproject.com/en/2.1/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/2.1/topics/i18n/

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_L10N = True
USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.1/howto/static-files/

STATIC_URL = '/static/'


# Logging

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'default': {
            'format': '%(levelname)s %(asctime)s: %(name)s: %(message)s'
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'default',
        },
    },
    'loggers': {
        'django': {
            'handlers': LOGGING_HANDLERS,
            'level': 'INFO',
            'propagate': True,
        },
        'django.security': {
            'handlers': LOGGING_HANDLERS,
            'level': 'INFO',
            'propagate': True,
        },
        'django.request': {
            'handlers': LOGGING_HANDLERS,
            'level': 'ERROR',
            'propagate': True,
        },
        'djangobot': {
            'handlers': LOGGING_HANDLERS,
            'level': LOG_LEVEL,
            'propagate': False,
        },
        'sopelbot': {
            'handlers': LOGGING_HANDLERS,
            'level': LOG_LEVEL,
            'propagate': False,
        }
    },
}
