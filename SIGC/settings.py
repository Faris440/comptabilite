"""
Django settings for SIGC project.

Generated by 'django-admin startproject' using Django 5.2.

For more information on this file, see
https://docs.djangoproject.com/en/5.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/5.2/ref/settings/
"""


from pathlib import Path
import environ
from email.utils import parseaddr

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

env = environ.Env()
environ.Env.read_env(env_file=str(BASE_DIR / "SIGC" / ".env.local"))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = env.str("SECRET_KEY")

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = env.bool("DEBUG", default=True)  # False pour désactiver le débogage
ONLINE = env.bool("ONLINE", default=False)
ADMINS = tuple(parseaddr(email) for email in env.list("ADMINS"))
MANAGERS = tuple(parseaddr(email) for email in env.list("MANAGERS"))
GENERATED_PASSWORD_LENGTH = env.int("GENERATED_PASSWORD_LENGTH", default=15)
LIST_MAX_ROWS = env.int("LIST_MAX_ROWS", default=10)
FILE_UPLOAD_MAX_MEMORY_SIZE = env.int("FILE_UPLOAD_MAX_MEMORY_SIZE")

LOGIN_URL = "/login/"
LOGOUT_REDIRECT_URL = "/login/"
LOGIN_REDIRECT_URL = "/"

ALLOWED_HOSTS = env.list("ALLOWED_HOSTS")

PUBLIC_NAMED_URLS = (
    "user-login",
    "password-reset-request",
    "password-reset-request-done",
    "password_reset_confirm",
    "password-reset-complete",
    "user-signup",
    "user-set-password",
    "mptt",
)  # vues publiques

ONLY_SUPERUSER_URLS = (
    "user-activation",
)  # vues accessibles que par superuser **Doesn't work**
ONLY_ADMINS_URLS = ()  # vues accessibles que par simple admin **Doesn't work**
SITE_ID = 1


# Application definition

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.humanize",
    "channels",
    "formset",
    "django_feather",
    "import_export",
    "django_filters",
    "fontawesomefree",
    "ckeditor",
    "notifications",
    "django_bootstrap5",
    "xauth.apps.XauthConfig",
    "parameter.apps.ParameterConfig",
    "ie_app.apps.IeAppConfig",
    
]

MIDDLEWARE = [
    "csp.middleware.CSPMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "django_permissions_policy.PermissionsPolicyMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "SIGC.middlewares.LoginRequiredMiddleware",
]

if ONLINE:

    pass

ROOT_URLCONF = "SIGC.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [
            BASE_DIR / "SIGC/templates",
            BASE_DIR / "parameter/templates",
            BASE_DIR / "xauth/templates",
            BASE_DIR / "ie_app/templates",
        ],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "SIGC.context_processors.get_icons_size",  # Size
            ],
        },
    },
]

WSGI_APPLICATION = "SIGC.wsgi.application"


CKEDITOR_CONFIGS = {
    'default': {
        'toolbar': 'full',
        'height': 300,
        'width': 'auto',
    },
}


USE_ONLINE_DB = env.bool("USE_ONLINE_DB")
USE_DB_POOL = env.bool("USE_DB_POOL")
if USE_ONLINE_DB:
    DATABASES = {
        "default": {
            "NAME": env.str("DB_NAME"),
            "USER": env.str("DB_USERNAME"),
            "PASSWORD": env.str("DB_PASSWORD"),
            "HOST": env.str("DB_HOST"),
            "PORT": env.int("DB_PORT"),
        }
    }
    DATABASES["default"]["ENGINE"] = (
        f"dj_db_conn_pool.backends.{env.str('DB_ENGINE')}"
        if USE_DB_POOL
        else f"django.db.backends.{env.str('DB_ENGINE')}"
    )
    if USE_DB_POOL:
        DATABASES["default"]["POOL_OPTIONS"] = {
            "POOL_SIZE": env.int("DB_POOL_SIZE"),
            "MAX_OVERFLOW": env.int("DB_POOL__MAX_OVERFLOW"),
            "RECYCLE": env.int("DB_POOL_RECYCLE"),
        }
else:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": BASE_DIR / "db.sqlite3",
        }
    }


# Password validation
# https://docs.djangoproject.com/en/5.0/ref/settings/#auth-password-validators

PASSWORD_MIN_LENGTH = env.int("PASSWORD_MIN_LENGTH")
AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
        "OPTIONS": {
            "min_length": PASSWORD_MIN_LENGTH,
        },
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]


# Internationalization
# https://docs.djangoproject.com/en/5.0/topics/i18n/

LANGUAGE_CODE = "fr-bf"

TIME_ZONE = "UTC"

USE_I18N = True

USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.0/howto/static-files/

STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
STATICFILES_DIRS = [
    BASE_DIR / "SIGC/static",
        ('node_modules', BASE_DIR / 'node_modules'),

]
MEDIA_ROOT = BASE_DIR / "mediafiles"
MEDIA_URL = "/media/"



# CKEditor Settings
CKEDITOR_UPLOAD_PATH = 'uploads/'
CKEDITOR_IMAGE_BACKEND = "pillow"
CKEDITOR_JQUERY_URL = '//ajax.googleapis.com/ajax/libs/jquery/2.1.1/jquery.min.js' 
CKEDITOR_CONFIGS = {
    'default':
        {
            'toolbar': 'full',
            'width': 'auto',
            'extraPlugins': ','.join([
                'codesnippet',
            ]),
        },
}

# Default primary key field type
# https://docs.djangoproject.com/en/5.0/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"


DEFAULT_FROM_EMAIL = env.str("EMAIL_SERVER")
EMAIL_SUBJECT_PREFIX = env.str("EMAIL_SUBJECT_PREFIX")
USE_EMAIL = env.bool("USE_EMAIL")
if USE_EMAIL:
    EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
    EMAIL_HOST = env.str("EMAIL_HOST")
    EMAIL_HOST_PASSWORD = env.str("EMAIL_HOST_PASSWORD")
    EMAIL_HOST_USER = env.str("EMAIL_HOST_USER")
    EMAIL_PORT = env.int("EMAIL_PORT")
    EMAIL_USE_LOCALTIME = True
    EMAIL_USE_TLS = env.bool("EMAIL_USE_TLS")
    EMAIL_USE_SSL = env.bool("EMAIL_USE_SSL")
    SERVER_EMAIL = env.str("EMAIL_SERVER")
else:
    EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"


# Cache memory
USE_MEMCACHE = env.bool("USE_MEMCACHE")
USE_REDIS = env.bool("USE_REDIS")
USE_DB_CACHE = env.bool("USE_DB_CACHE")
if USE_MEMCACHE:
    MEMCACHE_HOST = env.str("MEMCACHE_HOST")
    MEMCACHE_PORT = env.int("MEMCACHE_PORT")
    location = f"{MEMCACHE_HOST}:{MEMCACHE_PORT}"
    CACHES = {
        "default": {
            "BACKEND": "django.core.cache.backends.memcached.PyMemcacheCache",
            "LOCATION": location,
        }
    }
elif USE_REDIS:
    REDIS_HOST = env.str("REDIS_HOST")
    REDIS_PORT = env.int("REDIS_PORT")
    REDIS_USERNAME = env.str("REDIS_USERNAME")
    REDIS_PASSWORD = env.str("REDIS_PASSWORD")
    location = (
        f"redis://{REDIS_USERNAME}:{REDIS_PASSWORD}@{REDIS_HOST}:{REDIS_PORT}"
        if REDIS_USERNAME and REDIS_PASSWORD
        else f"redis://{REDIS_HOST}:{REDIS_PORT}"
    )
    CACHES = {
        "default": {
            "BACKEND": "django.core.cache.backends.redis.RedisCache",
            "LOCATION": location,
        }
    }
elif USE_DB_CACHE:  # RUN python manage.py createcachetable
    location = env.str("DB_TABLE_NAME")
    CACHES = {
        "default": {
            "BACKEND": "django.core.cache.backends.db.DatabaseCache",
            "LOCATION": location,
        }
    }
else:
    CACHES = {
        "default": {
            "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
            "LOCATION": "unique-snowflake",
        }
    }
CACHE_MIDDLEWARE_ALIAS = "default"
CACHE_MIDDLEWARE_KEY_PREFIX = env.str("CACHE_KEY_PREFIX")
CACHE_MIDDLEWARE_SECONDS = env.int("CACHE_SECONDS")

if ONLINE:
    SESSION_ENGINE = "django.contrib.sessions.backends.cache"
else:
    SESSION_ENGINE = "django.contrib.sessions.backends.file"
    SESSION_FILE_PATH = BASE_DIR / "mediafiles/cache"  # TODO created it in mode dev


ACTIVATE_SECURITY = env.bool("ACTIVATE_SECURITY")
if ACTIVATE_SECURITY:
    CSRF_COOKIE_SECURE = True
    SESSION_COOKIE_SECURE = True
    SECURE_HSTS_SECONDS = 6 * 2_592_000
    SECURE_HSTS_PRELOAD = True
    SECURE_SSL_REDIRECT = True
    SESSION_COOKIE_AGE = env.int("SESSION_COOKIE_AGE")
    SESSION_EXPIRE_AT_BROWSER_CLOSE = env.bool("SESSION_EXPIRE_AT_BROWSER_CLOSE")
    PASSWORD_RESET_TIMEOUT = env.int("PASSWORD_RESET_TIMEOUT")
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    CSRF_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Strict"
    SESSION_COOKIE_NAME = "__Secure-sessionid"
    CSRF_COOKIE_NAME = "__Secure-csrftoken"
    SECURE_CONTENT_TYPE_NOSNIFF = True


CSP_DEFAULT_SRC = ["'none'"]
CSP_BASE_URI = ["'self'"]
CSP_IMG_SRC = ["*", "'self'", "data:"]
CSP_STYLE_SRC = [
    "'self'",
    "'unsafe-inline'",
    "https://cdn.jsdelivr.net",
    "https://fonts.googleapis.com",
    "https://fonts.googleapis.com/css",
    'https://cdnjs.cloudflare.com',
]
CSP_CONNECT_SRC = ["*"]
CSP_SCRIPT_SRC = [
    "'self'",
    "'unsafe-inline'",
    "'unsafe-eval'",
    "https://cdn.jsdelivr.net",
    'https://cdnjs.cloudflare.com',
    'https://code.jquery.com',
]
CSP_FORM_ACTION = ["'self'"]
CSP_OBJECT_SRC = ["'none'"]
CSP_FRAME_ANCESTORS = ["'self'"]
CSP_FONT_SRC = [
    "'self'",
    "https://fonts.googleapis.com/css",
    "https://fonts.googleapis.com",
    "https://fonts.gstatic.com",
    'https://cdn.jsdelivr.net',
]
CSP_INCLUDE_NONCE_IN = ["script-src"]
# CSP_REQUIRE_TRUSTED_TYPES_FOR = ["'script'"]

PERMISSIONS_POLICY = {
    "accelerometer": [],
    # "ambient-light-sensor": [],
    "autoplay": [],
    "camera": [],
    "display-capture": [],
    # "document-domain": [],
    "encrypted-media": [],
    "fullscreen": [],
    "geolocation": [],
    "gyroscope": [],
    "interest-cohort": [],
    "magnetometer": [],
    "microphone": [],
    "midi": [],
    "payment": [],
    "usb": [],
}

# EASY-AUDIT settings keys
DJANGO_EASY_AUDIT_READONLY_EVENTS = True

# Phone Number Field
PHONENUMBER_DB_FORMAT = "INTERNATIONAL"
PHONENUMBER_DEFAULT_FORMAT = "NATIONAL"
PHONENUMBER_DEFAULT_REGION = "BF"


AUTH_USER_MODEL = "xauth.User"

PDFKIT_OPTIONS = {
    "page-size": "A4",
    "encoding": "UTF-8",
}


LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
        },
    },
    "root": {
        "handlers": ["console"],
        "level": "DEBUG",
    },
}

TINYMCE_DEFAULT_CONFIG = {
    "height": "320px",
    "width": "80%",
    "margin": "auto",
    "menubar": "file edit view insert format tools table help",
    "plugins": "advlist autolink lists link image charmap print preview anchor searchreplace visualblocks code "
    "fullscreen insertdatetime media table paste code help wordcount spellchecker",
    "toolbar": "undo redo | bold italic underline strikethrough | fontselect fontsizeselect formatselect | alignleft "
    "aligncenter alignright alignjustify | outdent indent |  numlist bullist checklist | forecolor "
    "backcolor casechange permanentpen formatpainter removeformat | pagebreak | charmap emoticons | "
    "fullscreen  preview save print | insertfile image media pageembed template link anchor codesample | "
    "a11ycheck ltr rtl | showcomments addcomment code",
    "custom_undo_redo_levels": 10,
    "language": "fr_BF",  # To force a specific language instead of the Django current language.
}
