import os
import environ
from django.urls import reverse_lazy, reverse


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

environment = os.getenv('PRODUCTION', False)

env = environ.Env()
environ.Env.read_env(os.path.join(BASE_DIR, ".env"))

SECRET_KEY = 'd$+1pmsjxraw8n0@n0ksa^59_h(b6d@leujqgb%nqx3b6v-lol'
DEBUG = env('DEBUG', bool, default=False)

if DEBUG:
    ALLOWED_HOSTS = ['*']
else:
    ALLOWED_HOSTS = ['127.0.0.1', '46.17.248.58', '0.0.0.0']


INSTALLED_APPS = [
    'django_dramatiq',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django_extensions',
    'mptt',
    'tasks',
    'users',
    'comments',
    'bootstrap4',
    'stronghold',
    'notifications',
    'crispy_forms',
]

CRISPY_TEMPLATE_PACK = 'uni_form'

MIDDLEWARE = [
    'stronghold.middleware.LoginRequiredMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'crm.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
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

WSGI_APPLICATION = 'crm.wsgi.application'

if env('USE_POSTGRES', bool, default=False):
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql_psycopg2',
            'NAME': env('DB_NAME', str),
            'USER': env('DB_USER', str),
            'PASSWORD': env('DB_PASSWORD', str),
            'HOST': env('DB_HOST', str),
            'PORT': env('DB_PORT', str),
        }
    }
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
        }
    }


AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',},
]


LANGUAGE_CODE = 'ru-ru'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

MEDIA_ROOT = os.path.join(BASE_DIR, 'media-files')
MEDIA_URL = '/media/'

STATICFILES_DIRS = [
    os.path.join(BASE_DIR, "static"),
]

DRAMATIQ_BROKER = {
    "BROKER": "dramatiq.brokers.redis.RedisBroker",
    "OPTIONS": {"url": "redis://localhost:6379",},
    "MIDDLEWARE": [
        "dramatiq.middleware.Prometheus",
        "dramatiq.middleware.AgeLimit",
        "dramatiq.middleware.TimeLimit",
        "dramatiq.middleware.Callbacks",
        "dramatiq.middleware.Retries",
        "django_dramatiq.middleware.AdminMiddleware",
        "django_dramatiq.middleware.DbConnectionsMiddleware",
    ],
}

DRAMATIQ_TASKS_DATABASE = "default"

LOGIN_REDIRECT_URL = reverse_lazy('tasks:task-list')
LOGOUT_REDIRECT_URL = reverse_lazy('login')
# STRONGHOLD
STRONGHOLD_DEFAULTS = True
STRONGHOLD_PUBLIC_URLS = ("/accounts/password_reset/",)

AUTH_USER_MODEL = 'users.User'

MESSAGE_STORAGE = 'django.contrib.messages.storage.session.SessionStorage'