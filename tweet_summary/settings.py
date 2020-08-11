"""
Django settings for tweet_summary project.

Generated by 'django-admin startproject' using Django 2.2.7.

For more information on this file, see
https://docs.djangoproject.com/en/2.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/2.2/ref/settings/
"""

import os
import dj_database_url
from celery.schedules import crontab

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
from celery.schedules import crontab

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/2.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '0j^cnixv3svemc5_83*dv^-09%-lra57pybco#b&(arnr_jbjg'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

SITE_EMAIL = 'alexkay72850@gmail.com'
EMAIL_HOST_USER = 'alexkay72850@gmail.com'
EMAIL_HOST_PASSWORD = 'alexkay728'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_USE_SSL = False

ALLOWED_HOSTS = ['tweet-summary.herokuapp.com', 'tweet-summary.socialmediapulsemonitor.com', 'tweet-summary.thesocialmediapulse.com', 'ai.newssumarization.com', '*']

LOGIN_REDIRECT_URL = '/support/login'

# Application definition

INSTALLED_APPS = [
    'api_manager.apps.ApiManagerConfig',
    'dashboard.apps.DashboardConfig',
    'app_support.apps.AppSupportConfig',
    'subscriber',
    'django_celery_beat',
    'rest_framework',
    'corsheaders',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles'
]

MIDDLEWARE = [
    'django.middleware.csrf.CsrfViewMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'tweet_summary.urls'

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.memcached.MemcachedCache',
        'LOCATION': '127.0.0.1:11211',
    }
}

CORS_ORIGIN_WHITELIST = [
    'https://tweet-summary.herokuapp.com',
    'http://tweet-summary.herokuapp.com',
    'http://tweet-summary.socialmediapulsemonitor.com',
    'http://tweet-summary.thesocialmediapulse.com',
    'http://localhost:8000',
    'http://ai.newssumarization.com'
]

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

WSGI_APPLICATION = 'tweet_summary.wsgi.application'


# Database
# https://docs.djangoproject.com/en/2.2/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
    # 'default':{
    #     'ENGINE': 'django.db.backends.postgresql_psycopg2',
    #     'NAME': os.environ.get('DATABASE'),
    #     'USER': os.environ.get('USER'),
    #     'PASSWORD': os.environ.get('PASSWORD'),
    #     'HOST': os.environ.get('HOST'),
    #     'PORT': os.environ.get('PORT'),
    # }
}

db_from_env = dj_database_url.config(conn_max_age=600)
DATABASES['default'].update(db_from_env)


# Password validation
# https://docs.djangoproject.com/en/2.2/ref/settings/#auth-password-validators

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

# CELERY STUFF
CELERY_BROKER_URL =  'redis://localhost:6379'
CELERY_RESULT_BACKEND =  'redis://localhost:6379'
CELERY_ACCEPT_CONTENT = ['application/json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = 'Asia/Kolkata'
CELERY_BEAT_SCHEDULE = {
    'send-ready-call': {
        'task': 'subscriber.tasks.ready',
        'schedule': 60.0,
    },
    'send-tweet-analysis-everyday': {
        'task': 'subscriber.tasks.daily_service',
        'schedule': crontab(day_of_week="0-6", hour=20, minute=0),
    },
    # 'send-tweet-analysis-everyday': {
    #     'task': 'subscriber.tasks.daily_service',
    #     'schedule': 60.0,
    # },
}

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True

MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
MEDIA_URL = '/media/'

STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

STATIC_URL = '/static/'

STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

# STATICFILES_DIRS = [
#     os.path.join(BASE_DIR, 'dashboard/static'),
#     os.path.join(BASE_DIR, 'subscriber/static'),
#     os.path.join(BASE_DIR, 'app_support/static')
# ]
