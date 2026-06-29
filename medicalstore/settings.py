from pathlib import Path
import dj_database_url
from decouple import config, Csv

BASE_DIR = Path(__file__).resolve().parent.parent

# ─── Security ──────────────────────────────────────────────────────────────────
SECRET_KEY = config('SECRET_KEY')
DEBUG = config('DEBUG', default=False, cast=bool)
ALLOWED_HOSTS = config('ALLOWED_HOSTS', default='localhost,127.0.0.1', cast=Csv())

_csrf_origins = config('CSRF_TRUSTED_ORIGINS', default='')
CSRF_TRUSTED_ORIGINS = [o.strip() for o in _csrf_origins.split(',') if o.strip()]

CART_SESSION_ID = 'cart'

# ─── Apps ──────────────────────────────────────────────────────────────────────
INSTALLED_APPS = [
    'modeltranslation',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'cloudinary_storage',
    'django.contrib.staticfiles',
    'cloudinary',
    'products',
    'cart',
    'pages',
    'orders',
    'accounts',
]

# ─── Middleware ─────────────────────────────────────────────────────────────────
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',  # serve static files in production
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'medicalstore.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.template.context_processors.i18n',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'cart.context_processors.cart',
                'pages.context_processors.site_settings',
            ],
        },
    },
]

WSGI_APPLICATION = 'medicalstore.wsgi.application'

# ─── Email ─────────────────────────────────────────────────────────────────────
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
# EMAIL_USE_SSL = True
EMAIL_USE_SSL = False
EMAIL_USE_TLS = True

ADMIN_EMAIL = config('ADMIN_EMAIL', default='admin@example.com')
DEFAULT_FROM_EMAIL = config('DEFAULT_FROM_EMAIL', default='info@example.com')
SERVER_EMAIL = config('DEFAULT_FROM_EMAIL', default='info@example.com')

# Used by send_email_directly() in orders/views.py
EMAIL_HOST = config('SMTP_HOST', default='smtp.gmail.com')
EMAIL_PORT = config('SMTP_PORT', default=587, cast=int)
EMAIL_HOST_USER = config('SMTP_EMAIL', default='')
EMAIL_HOST_PASSWORD = config('SMTP_PASSWORD', default='')

# ─── Database ──────────────────────────────────────────────────────────────────
# Reads DATABASE_URL from environment; falls back to SQLite for local development.
DATABASES = {
    'default': dj_database_url.parse(
        config('DATABASE_URL', default=f"sqlite:///{BASE_DIR / 'db.sqlite3'}"),
        conn_max_age=600,
    )
}

# ─── Password validation ───────────────────────────────────────────────────────
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# ─── Internationalisation ──────────────────────────────────────────────────────
LANGUAGE_CODE = 'en'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_L10N = True
USE_TZ = True

LANGUAGES = [
    ('en', 'English'),
    ('fr', 'French'),
]

LOCALE_PATHS = [
    BASE_DIR / 'locale',
]

# ─── Static & Media ────────────────────────────────────────────────────────────
STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_ROOT = BASE_DIR / 'staticfiles'

# Use compressed+hashed filenames in production; plain storage in dev
STATICFILES_STORAGE = (
    'whitenoise.storage.CompressedManifestStaticFilesStorage'
    if not DEBUG
    else 'django.contrib.staticfiles.storage.StaticFilesStorage'
)

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# ─── Cloudinary (image storage) ────────────────────────────────────────────────
CLOUDINARY_STORAGE = {
    'CLOUD_NAME': config('CLOUDINARY_CLOUD_NAME', default=''),
    'API_KEY': config('CLOUDINARY_API_KEY', default=''),
    'API_SECRET': config('CLOUDINARY_API_SECRET', default=''),
}

if all([
    config('CLOUDINARY_CLOUD_NAME', default=''),
    config('CLOUDINARY_API_KEY', default=''),
    config('CLOUDINARY_API_SECRET', default=''),
]):
    DEFAULT_FILE_STORAGE = 'cloudinary_storage.storage.MediaCloudinaryStorage'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# ─── Security headers ──────────────────────────────────────────────────────────
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'SAMEORIGIN'

# ─── Sessions ──────────────────────────────────────────────────────────────────
SESSION_COOKIE_AGE = 86400          # 24 hours
SESSION_SAVE_EVERY_REQUEST = True
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SECURE = not DEBUG   # HTTPS-only cookies in production

# ─── Auth ──────────────────────────────────────────────────────────────────────
LOGIN_URL = '/accounts/login/'
LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/'
