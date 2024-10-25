"""
Django settings for mysite project.

Generated by 'django-admin startproject' using Django 5.0.1.

For more information on this file, see
https://docs.djangoproject.com/en/5.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/5.0/ref/settings/
"""

import os
import dj_database_url
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()
# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Used for a default title
APP_NAME = 'Sports Replay Forum'

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ['SECRET_KEY']
API_PULL_TOKEN = os.getenv('API_PULL_TOKEN', 'fallback-token')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.environ.get('DEBUG', 'False').lower() == "true"

ALLOWED_HOSTS =  ['hotwatchsports2.onrender.com', '127.0.0.1']

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'home.apps.HomeConfig',
    'core.apps.CoreConfig',
    'users.apps.UsersConfig',

    'sports.f1.apps.F1Config',
    'sports.nations.apps.NationsConfig',
    'sports.champions.apps.ChampionsConfig',
    'sports.premier.apps.PremierConfig',
    'sports.motogp.apps.MotogpConfig',
    'sports.worldcup.apps.WorldcupConfig',

    # Extensions - installed with requirements.txt
    'django_extensions', 
    'crispy_forms',  
    'crispy_bootstrap5',  
    'rest_framework', 
]

# When we get to tagging

# When we get to crispy forms :)
CRISPY_ALLOWED_TEMPLATE_PACKS = "bootstrap5"
CRISPY_TEMPLATE_PACK = "bootstrap5"

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    "whitenoise.middleware.WhiteNoiseMiddleware",
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'sportsreplayforum.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR,'templates')],
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

WSGI_APPLICATION = 'sportsreplayforum.wsgi.application'


# Database
# https://docs.djangoproject.com/en/5.1/ref/settings/#databases


DATABASE_ENV = os.environ.get('DATABASE_ENV', 'local')

if DATABASE_ENV == 'local':
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }
elif DATABASE_ENV == 'render':
    database_url = os.environ.get('DATABASE_URL')
    DATABASES = {
        'default': dj_database_url.parse(database_url)
    }

# Password validation
# https://docs.djangoproject.com/en/5.0/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/5.0/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.0/howto/static-files/

STATIC_URL = 'static/'

STATICFILES_DIRS = [BASE_DIR / 'static']  
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"


""" STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'static'),
]
 """


REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework.authentication.BasicAuthentication',
        'rest_framework.authentication.SessionAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticatedOrReadOnly',
    )
}


LOGOUT_REDIRECT_URL = '/'
LOGIN_REDIRECT_URL = '/'

# Don't set default LOGIN_URL - let django.contrib.auth set it when it is loaded
# LOGIN_URL = '/users/login'

# Needed for 3.2 and later
# https://stackoverflow.com/questions/67783120/warning-auto-created-primary-key-used-when-not-defining-a-primary-key-type-by
DEFAULT_AUTO_FIELD = 'django.db.models.AutoField'

# https://coderwall.com/p/uzhyca/quickly-setup-sql-query-logging-django
# https://stackoverflow.com/questions/12027545/determine-if-django-is-running-under-the-development-server

'''  # Leave off for now
import sys
if (len(sys.argv) >= 2 and sys.argv[1] == 'runserver'):
    print('Running locally')
    LOGGING = {
        'version': 1,
        'disable_existing_loggers': False,
        'handlers': {
            'console': {
                'level': 'DEBUG',
                'class': 'logging.StreamHandler',
            }
        },
        'loggers': {
            'django.db.backends': {
                'handlers': ['console'],
                'level': 'DEBUG',
            },
        }
    }
'''

# Email settings
mail = os.environ.get("MAIL")
mail_pass = os.environ.get("MAIL_PASS")

EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = "smtp.ionos.co.uk"
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = mail
EMAIL_HOST_PASSWORD = mail_pass
DEFAULT_FROM_EMAIL = mail
EMAIL_SUBJECT_PREFIX = "Password Recovery"

