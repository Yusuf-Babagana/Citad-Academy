

import os
import dj_database_url
from pathlib import Path

import os
import dj_database_url

# Load environment variables
from dotenv import load_dotenv

load_dotenv()


# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-c#z2-e69^nqe9mdi-@$ao@39y$k$xof8$^oguy(+p4q_rn=dg3'

PAYSTACK_SECRET_KEY = 'sk_live_45b7c7f30643b43a738ada85dca6f095353e2f7d'

# Celery settings
CELERY_BROKER_URL = 'redis://localhost:6379/0'
CELERY_RESULT_BACKEND = 'redis://localhost:6379/0'
CELERY_TIMEZONE = 'UTC'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ["*"]


# Application definition

INSTALLED_APPS = [
    'user_management',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'rest_framework_simplejwt',
    'school_management',
    'class_management',
    'subject_management',
    'media_management',
    'exam_management',
    'student_management',
    'performance_tracking',
    'leaderboard',
    'corsheaders',
    'widget_tweaks',
    'ckeditor',
    'ckeditor_uploader',
    'markdownx',
    # 'resource',
    'payments',
    'subscription',
    'tinymce',
    'storages',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'subscription.check_subscription_middleware.CheckUserSubscription',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'iexam.urls'

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
                'user_management.context_processors.add_school_to_context',
            ],
        },
    },
]

WSGI_APPLICATION = 'iexam.wsgi.application'


# Django REST Framework settings
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
    # Add other global settings for DRF if needed
}

# Simple JWT settings
from datetime import timedelta
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=5),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=1),
    'ROTATE_REFRESH_TOKENS': False,
    'BLACKLIST_AFTER_ROTATION': False,

    'ALGORITHM': 'HS256',
    'SIGNING_KEY': SECRET_KEY,
    'VERIFYING_KEY': None,

    'AUTH_HEADER_TYPES': ('Bearer',),
    'AUTH_HEADER_NAME': 'HTTP_AUTHORIZATION',
    'USER_ID_FIELD': 'id',
    'USER_ID_CLAIM': 'user_id',
    'AUTH_TOKEN_CLASSES': ('rest_framework_simplejwt.tokens.AccessToken',),
    # Add other JWT settings if needed
}

# Database
# https://docs.djangoproject.com/en/4.2/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}


# Internationalization
# https://docs.djangoproject.com/en/4.2/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


CKEDITOR_CONFIGS = {
    'default': {
        'toolbar': 'Custom',
        'toolbar_Custom': [
            ['Bold', 'Italic', 'Underline'],
            ['NumberedList', 'BulletedList', '-', 'Outdent', 'Indent', '-', 'Blockquote'],
            ['JustifyLeft', 'JustifyCenter', 'JustifyRight', 'JustifyBlock'],
            ['Link', 'Unlink', 'Anchor'],
            ['Image2', 'Table', 'HorizontalRule', 'SpecialChar'],
            ['Styles', 'Format', 'Font', 'FontSize'],
            ['TextColor', 'BGColor'],
            ['Maximize'],
            ['Mathjax', 'CKEditorWiris'],  # Adjusted for MathType and Wiris
            ['Source'],
            # ... other toolbar items ...
        ],
        'height': 300,
        'width': '100%',
        'filebrowserUploadUrl': '/exam_management/ckeditor/upload/',
        'extraPlugins': ','.join([
            'mathjax',  # For math equations
            'image2',  # Enhanced image plugin
            'table', 'tableresize',  # For tables
            'clipboard', 'undo',  # Clipboard and undo functionality
            'liststyle', 'justify', 'link', 'autolink',  # Basic text styling and linking
            'ckeditor_wiris',  # MathType plugin integration
            # ... other plugins as needed ...
        ]),
        'mathJaxLib': 'https://cdnjs.cloudflare.com/ajax/libs/mathjax/2.7.7/MathJax.js?config=TeX-AMS_HTML',
        'removeDialogTabs': 'image:advanced;link:advanced',
        'removePlugins': 'exportpdf',
    },
}



# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.2/howto/static-files/


# CKEditor settings
CKEDITOR_UPLOAD_PATH = 'uploads/'
CKEDITOR_BASEPATH = "/static/ckeditor/ckeditor/"


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.2/howto/static-files/

STATIC_URL = '/static/'

# Use Path for STATIC_ROOT and STATICFILES_DIRS
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_DIRS = [
    BASE_DIR / 'static',
]

# CKEditor settings
CKEDITOR_UPLOAD_PATH = 'uploads/'
CKEDITOR_BASEPATH = "/static/ckeditor/ckeditor/"

# Media files
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media_files'

# Default primary key field type
# https://docs.djangoproject.com/en/4.2/ref/settings/#default-auto-field




# Use Path for STATIC_ROOT and check if 'staticfiles' is already part of BASE_DIR
# Note: STATIC_ROOT is not used when STATICFILES_STORAGE is set to an S3 backend
# STATIC_ROOT = BASE_DIR / 'staticfiles' if 'staticfiles' not in str(BASE_DIR) else BASE_DIR / 'staticfiles'


# Default primary key field type
# https://docs.djangoproject.com/en/4.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


AUTH_USER_MODEL = 'user_management.User'


CORS_ALLOW_ALL_ORIGINS = True
CORS_URLS_REGEX = r'^/api/.*$'
CSRF_TRUSTED_ORIGINS = ['https://www.iexams.net']



MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media_files')

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'  # SMTP server for Gmail
EMAIL_PORT = 587  # Port for sending email
EMAIL_USE_TLS = True  # Use TLS
EMAIL_HOST_USER = 'ibnsulemanjnr@gmail.com'
EMAIL_HOST_PASSWORD = 'suledtrust'

# Password validation
# https://docs.djangoproject.com/en/4.2/ref/settings/#auth-password-validators
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
        'OPTIONS': {
            'min_length': 8,
        }
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

TINYMCE_JS_URL = 'https://cdn.tiny.cloud/1/wtvyddp8vbf93fs3p0qosbhmvp0c78612suavj3oj4f1us95/tinymce/7/tinymce.min.js'
TINYMCE_COMPRESSOR = False

TINYMCE_DEFAULT_CONFIG = {
    'height': 480,
    'width': 800,
    'cleanup_on_startup': True,
    'custom_undo_redo_levels': 20,
    'selector': 'textarea',
    'theme': 'silver',
    'plugins': '''
        save link image media preview codesample table code lists fullscreen
        insertdatetime nonbreaking directionality searchreplace wordcount
        visualblocks visualchars fullscreen autolink lists charmap print hr
        anchor pagebreak tiny_mce_wiris  # Updated for clarity and correctness
        ''',
    'toolbar1': '''
        fullscreen preview bold italic underline | fontselect,
        fontsizeselect | forecolor backcolor | alignleft alignright |
        aligncenter alignjustify | numlist bullist outdent indent |
        table | link image media | codesample |
        tiny_mce_wiris_formulaEditor tiny_mce_wiris_formulaEditorChemistry
        ''',  # Ensure Wiris buttons are correctly identified
    'contextmenu': 'formats | link image',
    'menubar': True,
    'statusbar': True,
    'external_plugins': {
        'tiny_mce_wiris': '{Wiris Plugin URL}'  # Ensure this URL is correctly set as per Wiris documentation
    },
    'content_css': [
        '//www.tiny.cloud/css/codepen.min.css'
    ],
    'mathjax_config': {  # This section might need to be implemented through custom scripting if using MathJax independently
        'src': 'https://cdnjs.cloudflare.com/ajax/libs/mathjax/2.7.7/MathJax.js?config=TeX-AMS_HTML',
        'config': {
            'TeX': {
                'equationNumbers': {'autoNumber': 'AMS'},
                'extensions': ['AMSmath.js', 'AMSsymbols.js'],
            },
            'displayAlign': 'left',
            'displayIndent': '2em',
        },
    },
}