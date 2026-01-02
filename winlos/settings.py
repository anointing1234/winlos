from pathlib import Path
import os
import environ
from django.templatetags.static import static
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _
import environ
from redis.exceptions import ConnectionError as RedisConnectionError

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# ✅ EXPLICIT PATH (THIS IS THE KEY FIX)
environ.Env.read_env(BASE_DIR / ".env")


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.2/howto/deployment/checklist/
# Quick-start development settings
SECRET_KEY = os.getenv("SECRET_KEY", "unsafe-dev-key")
DEBUG = False

# ALLOWED_HOSTS = os.getenv("ALLOWED_HOSTS", "localhost,127.0.0.1").split(",")
# CSRF_TRUSTED_ORIGINS = os.getenv("CSRF_TRUSTED_ORIGINS", "http://localhost,http://127.0.0.1").split(",")
# DEBUG_PROPAGATE_EXCEPTIONS = False




# ALLOWED_HOSTS: only hostnames (no http/https)
ALLOWED_HOSTS = [
    "winlos-production.up.railway.app",
    "www.winlos-production.up.railway.app",
    "localhost",
    "127.0.0.1",
]


# CSRF_TRUSTED_ORIGINS: full scheme required
CSRF_TRUSTED_ORIGINS = [
    "https://winlos-production.up.railway.app",
    "https://www.winlos-production.up.railway.app",
]




LOGIN_URL = 'login'
ADMIN_LOGIN_URL = 'Admin_login'
# Application definition


# # Application definition
AUTH_USER_MODEL = "winlos_app.Account"


# --------------------------------------------------
# APPLICATIONS
# --------------------------------------------------
INSTALLED_APPS = [
    "unfold",
    "unfold.contrib.filters",
    "unfold.contrib.import_export",
    "unfold.contrib.guardian",
    "unfold.contrib.simple_history",
    "unfold.contrib.forms",
    "unfold.contrib.inlines",

    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.humanize",

    "winlos_app",
    "anymail",

    "storages", 
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

ROOT_URLCONF = 'winlos.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR,'core/templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'winlos.wsgi.application'


# Database
# https://docs.djangoproject.com/en/5.2/ref/settings/#databases




# --------------------------------------------------
# DATABASE
# --------------------------------------------------

# Database
if DEBUG:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": os.path.join(BASE_DIR, "db.sqlite3"),
        }
    }
else:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.postgresql",
            "NAME": os.getenv("DB_NAME"),
            "USER": os.getenv("DB_USER"),
            "PASSWORD": os.getenv("DB_PASSWORD"),
            "HOST": os.getenv("DB_HOST"),
            "PORT": os.getenv("DB_PORT", "5432"),
            "CONN_MAX_AGE": 900,
            "OPTIONS": {
            "sslmode": "require",  # important for Railway
        },
        }
    }



# Password validation
# https://docs.djangoproject.com/en/5.2/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/5.2/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.2/howto/static-files/

# --------------------------------------------------
# STATIC & MEDIA (CLOUDFLARE R2)
# --------------------------------------------------

# Use R2 only when NOT in Debug mode (Production)
# Static & media
if not DEBUG:
    AWS_ACCESS_KEY_ID = os.getenv("CLOUDFLARE_R2_ACCESS_KEY")
    AWS_SECRET_ACCESS_KEY = os.getenv("CLOUDFLARE_R2_SECRET_KEY")
    AWS_STORAGE_BUCKET_NAME = os.getenv("CLOUDFLARE_R2_BUCKET_NAME")
    AWS_S3_ENDPOINT_URL = os.getenv("CLOUDFLARE_R2_ENDPOINT_URL")
    AWS_S3_CUSTOM_DOMAIN = os.getenv("CLOUDFLARE_R2_PUBLIC_URL_DOMAIN")

    AWS_S3_REGION_NAME = "auto"
    AWS_S3_SIGNATURE_VERSION = "s3v4"
    AWS_DEFAULT_ACL = None
    AWS_QUERYSTRING_AUTH = False

    STORAGES = {
        "default": {
            "BACKEND": "storages.backends.s3.S3Storage",
            "OPTIONS": {"location": "media"},
        },
        "staticfiles": {
            "BACKEND": "storages.backends.s3.S3Storage",
            "OPTIONS": {"location": "static"},
        },
    }
else:
    STATIC_URL = "static/"
    STATIC_ROOT = BASE_DIR / "staticfiles"
    MEDIA_URL = "media/"
    MEDIA_ROOT = BASE_DIR / "media"

STATICFILES_DIRS = [BASE_DIR / "core" / "static"]


# Always set these when using R2 (even if DEBUG=True locally with R2)
if 'AWS_S3_CUSTOM_DOMAIN' in locals():
    STATIC_URL = f"https://{AWS_S3_CUSTOM_DOMAIN}/static/"
    MEDIA_URL = f"https://{AWS_S3_CUSTOM_DOMAIN}/media/"


if not DEBUG:
    # Additional headers
    SECURE_REFERRER_POLICY = "strict-origin-when-cross-origin"
    SECURE_CROSS_ORIGIN_OPENER_POLICY = "same-origin"

# Default primary key field type
# https://docs.djangoproject.com/en/5.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


# PAYSTACK_PUBLIC_KEY = os.environ.get("PAYSTACK_PUBLIC_KEY", "pk_test_xxxxx")
# PAYSTACK_SECRET_KEY = os.environ.get("PAYSTACK_SECRET_KEY", "sk_test_xxxxx")
# PAYSTACK_VERIFY_URL = "https://api.paystack.co/transaction/verify/"




SESSION_ENGINE = "django.contrib.sessions.backends.db"



AUTHENTICATION_BACKENDS = [
    'winlos_app.backends.EmailBackend',  # <-- your custom backend
    'django.contrib.auth.backends.ModelBackend',  # fallback
]



# --------------------------------------------------
# EMAIL (RESEND)
# --------------------------------------------------
DEFAULT_FROM_EMAIL = "info@winlosacademy.com"
EMAIL_BACKEND = "anymail.backends.resend.EmailBackend"
ANYMAIL = {"RESEND_API_KEY": os.getenv("RESEND_API_KEY")}




# --------------------------------------------------
# SECURITY (PRODUCTION ONLY)
# --------------------------------------------------
if not DEBUG:
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
    SECURE_SSL_REDIRECT = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_BROWSER_XSS_FILTER = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
    X_FRAME_OPTIONS = 'DENY'
    SECURE_HSTS_SECONDS = 31536000  # 1 year
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True


PAYSTACK_PUBLIC_KEY = os.getenv("PAYSTACK_PUBLIC_KEY")
PAYSTACK_SECRET_KEY = os.getenv("PAYSTACK_SECRET_KEY")
PAYSTACK_BASE_URL = "https://api.paystack.co"



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
        "level": "INFO",
    },
}

# ======================
# DJANGO UNFOLD SETTINGS
# ======================

UNFOLD = {
    # ---- Branding ----
    "SITE_HEADER": "Winlos Academy Admin",
    "SITE_TITLE": "Winlos Academy Admin Panel",
    "SITE_SUBHEADER": "Manage courses, lessons, exams, and users easily.",
    "SITE_URL": "/",  # link logo back to homepage

    # ---- Logo / Icons (light & dark mode support) ----
    "SITE_ICON": {
        "light": lambda request: static("assets/img/preloader.png"),
        "dark": lambda request: static("assets/images/logo/winlos_logo_white.png"),
    },
    "SITE_LOGO": {
        "light": lambda request: static("assets/img/preloader.png"),
        "dark": lambda request: static("assets/images/logo/winlos_logo_white.png"),
    },

    # ---- Dashboard ----
    "DASHBOARD": {
        "show_search": True,
        "show_all_applications": False,
        "cards": [
            {
                "title": _("Users"),
                "icon": "group",
                "link": reverse_lazy("admin:winlos_app_account_changelist"),
                "description": _("Manage all registered students and instructors."),
            },
            {
                "title": _("Courses"),
                "icon": "school",
                "link": reverse_lazy("admin:winlos_app_course_changelist"),
                "description": _("Create, edit, and monitor courses."),
            },
            {
                "title": _("Enrollments"),
                "icon": "how_to_reg",
                "link": reverse_lazy("admin:winlos_app_enrollment_changelist"),
                "description": _("View and manage user course enrollments."),
            },
            {
                "title": _("Lessons"),
                "icon": "play_circle",
                "link": reverse_lazy("admin:winlos_app_lesson_changelist"),
                "description": _("Manage course lessons and videos."),
            },
            {
                "title": _("Progress"),
                "icon": "bar_chart",
                "link": reverse_lazy("admin:winlos_app_courseprogress_changelist"),
                "description": _("Track user progress across lessons and courses."),
            },
            {
                "title": _("Exams"),
                "icon": "assignment",
                "link": reverse_lazy("admin:winlos_app_exam_changelist"),
                "description": _("Create and manage course exams."),
            },
            {
                "title": _("Certificates"),
                "icon": "verified",
                "link": reverse_lazy("admin:winlos_app_certificate_changelist"),
                "description": _("View and issue course certificates."),
            },
            {
                "title": _("Auth Codes"),
                "icon": "vpn_key",
                "link": reverse_lazy("admin:winlos_app_authcode_changelist"),
                "description": _("Manage verification and password reset codes."),
            },
        ],
    },

    # ---- Sidebar ----
    "SIDEBAR": {
        "show_search": True,
        "show_all_applications": False,
        "navigation": [
            {
                "title": _("Main Management"),
                "icon": "dashboard",
                "collapsible": False,
                "items": [
                    {
                        "title": _("Users"),
                        "icon": "group",
                        "link": reverse_lazy("admin:winlos_app_account_changelist"),
                    },
                    {
                        "title": _("Courses"),
                        "icon": "school",
                        "link": reverse_lazy("admin:winlos_app_course_changelist"),
                    },
                    {
                        "title": _("Enrollments"),
                        "icon": "how_to_reg",
                        "link": reverse_lazy("admin:winlos_app_enrollment_changelist"),
                    },
                    {
                        "title": _("Lessons"),
                        "icon": "play_circle",
                        "link": reverse_lazy("admin:winlos_app_lesson_changelist"),
                    },
                    {
                        "title": _("Lesson Progress"),
                        "icon": "check_circle",
                        "link": reverse_lazy("admin:winlos_app_lessonprogress_changelist"),
                    },
                    {
                        "title": _("Course Progress"),
                        "icon": "bar_chart",
                        "link": reverse_lazy("admin:winlos_app_courseprogress_changelist"),
                    },
                    {
                        "title": _("Exams"),
                        "icon": "assignment",
                        "link": reverse_lazy("admin:winlos_app_exam_changelist"),
                    },
                    {
                        "title": _("Certificates"),
                        "icon": "verified",
                        "link": reverse_lazy("admin:winlos_app_certificate_changelist"),
                    },
                    {
                        "title": _("Auth Codes"),
                        "icon": "vpn_key",
                        "link": reverse_lazy("admin:winlos_app_authcode_changelist"),
                    },
                ],
            },
            {
                "title": _("Q&A Management"),
                "icon": "help",
                "collapsible": True,
                "items": [
                    {
                        "title": _("Questions"),
                        "icon": "question_answer",
                        "link": reverse_lazy("admin:winlos_app_examquestion_changelist"),
                    },
                    {
                        "title": _("Answers"),
                        "icon": "chat",
                        "link": reverse_lazy("admin:winlos_app_examoption_changelist"),
                    },
                    {
                        "title": _("Exam Attempts"),
                        "icon": "assignment_turned_in",
                        "link": reverse_lazy("admin:winlos_app_examattempt_changelist"),
                    },
                ],
            },
        ],
    },
}