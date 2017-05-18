# -*- coding: utf-8 -*-
from data_stores import *
import os.path
import requests
import sys

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir))
PROJECT_ROOT = BASE_DIR

# this is a little goofy,  should be simpler. -dv

project = lambda: os.path.dirname(os.path.join(os.path.realpath(__file__), os.path.pardir, os.path.pardir))
location = lambda x: os.path.join(str(project()), os.path.pardir, str(x))

WSGI_APPLICATION = 'r2d2.wsgi.application'

ADMINS = (
    ('Matt Laszuk', 'matt.laszuk@gmail.com'),
    ('Deno Vichas', 'deno@fullstacksystems.com')

)
MANAGERS = ADMINS

SECRET_KEY = 'localvay&e&9hdwo_bniq-$z0j64q4w27-fm58nu9!m+i$nc0e!*!o0'

EMAIL_USE_TLS = True
EMAIL_HOST = 'email-smtp.us-east-1.amazonaws.com'
EMAIL_HOST_PASSWORD = 'AhhBbt76BJLFSky4xbZ3RNt0KRntU8FnHAuCxHdeJ7RG'
EMAIL_HOST_USER = 'AKIAJKORSLH4UBCGMXVQ'
EMAIL_PORT = 587
DEFAULT_FROM_EMAIL = '"HelloSales" <hello@hello-sales.com>'

FORCE_SCRIPT_NAME = ""
TIME_ZONE = "US/Eastern"
LANGUAGE_CODE = 'en'

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = False
USE_L10N = True
DEFAULT_DATE_FORMAT = '%B %d, %Y'

# This is defined here as a do-nothing function because we can't import
# django.utils.translation -- that module depends on the settings.
gettext_noop = lambda s: s


# A sample logging configuration. The only tangible logging
# performed by this configuration is to send an email to
# the site admins on every HTTP 500 error when DEBUG=False.
# See http://docs.djangoproject.com/en/dev/topics/logging for
# more details on how to customize your logging configuration.
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'standard': {
            'format': "[%(asctime)s] %(levelname)s [%(name)s:%(lineno)s] %(message)s",
            'datefmt': "%d/%b/%Y %H:%M:%S"
        },
    },
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse'
        }
    },
    'handlers': {
        'mail_admins': {
            'level': 'ERROR',
            'filters': ['require_debug_false'],
            'class': 'django.utils.log.AdminEmailHandler'
        },
        'applogfile': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': os.path.join(PROJECT_ROOT, 'r2d2.log'),
            'maxBytes': 1024*1024*15,  # 15MB
            'backupCount': 10,
            'formatter': 'standard'
        }
    },
    'loggers': {
        'django.request': {
            'handlers': ['mail_admins'],
            'level': 'ERROR',
            'propagate': True
        },
        '': {
            'handlers': ['applogfile'],
            'level': 'INFO'
        }
    }
}


# here is all the languages supported by the CMS
PAGE_LANGUAGES = (
    ('en', gettext_noop('English')),
    # ('es', gettext_noop('Spanish')),
)

PAGE_DEFAULT_TEMPLATE = 'pages/base.html'

PAGE_TEMPLATES = (
    ('pages/base.html', 'base'),
    ('pages/email-user.html', 'email-user'),
    ('pages/email-user-second.html', 'email-user-second'),
    ('pages/email-admin.html', 'email-admin'),
    ('pages/landing.html', 'landing'),
    ('pages/email-insight.html', 'email-insight'),
    ('email-account.html', 'email-account'),
)

PAGE_USE_SITE_ID = True

MEDIA_ROOT = location(os.path.join("site_media", "media"))
MEDIA_URL = '/media/'

STATIC_ROOT = location(os.path.join("site_media", "static"))

STATIC_URL = "/static/"
STATICFILES_DIRS = [
    location("static"),
]
STATICFILES_FINDERS = (
    "django.contrib.staticfiles.finders.FileSystemFinder",
    "django.contrib.staticfiles.finders.AppDirectoriesFinder",
    "compressor.finders.CompressorFinder",
)

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.BrokenLinkEmailsMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.common.CommonMiddleware',
    # 'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    # 'django.middleware.doc.XViewMiddleware',
)

CORS_ORIGIN_ALLOW_ALL = True
CORS_ALLOW_HEADERS = (
    'x-requested-with',
    'content-type',
    'accept',
    'origin',
    'authorization',
    'authentication',
    # 'x-csrftoken',
    # 'x-device-version',
    # 'x-app-version',
    # 'x-app-id',
    # 'x-device-model',
    # 'x-device-platform',
)

CORS_EXPOSE_HEADERS = (
    'content-disposition',
    # 'x-mobile-version',
)

ROOT_URLCONF = 'r2d2.urls'

TEMPLATE_CONTEXT_PROCESSORS = [
    'django.contrib.auth.context_processors.auth',
    'django.core.context_processors.debug',
    'django.core.context_processors.i18n',
    'django.core.context_processors.media',
    'django.core.context_processors.request',
    'django.contrib.messages.context_processors.messages',
    'django.core.context_processors.static',
    'basic_cms.context_processors.media',
    'r2d2.context.site',
]

PROJECT_APPS = (
    'r2d2.accounts',
    'r2d2.common_layer',
    'r2d2.data_importer',
    'r2d2.emails',
    'r2d2.etsy_api',
    'r2d2.insights',
    'r2d2.notifications',
    'r2d2.shopify_api',
    'r2d2.squareup_api',
    'r2d2.stripe_api',
    'r2d2.utils',
)

INSTALLED_APPS = (
     'basic_cms',
     'compressor',
     'constance',
     'constance.backends.database',
     'corsheaders',
     'django.contrib.auth',
     'django.contrib.contenttypes',
     'django.contrib.sessions',
     'django.contrib.sites',
     'django.contrib.messages',
     'django.contrib.staticfiles',
     'django.contrib.humanize',
     'django_extensions',
     'djcelery_email',
     'django_su',
     'django.contrib.admin',
     'djmoney_rates',
     'django_mongoengine',
     'django_mongoengine.admin_support',
     'django_jenkins',
     # 'mptt',
     'grappelli',
     'filebrowser',
     # 'modeltranslation',
     'raven.contrib.django.raven_compat',
     'rest_framework_swagger',
     'rest_framework',
     'rest_framework.authtoken',
     'sorl.thumbnail',
     'taggit',
     'templateaddons',
     "tinymce",
     'ydcommon'
) + PROJECT_APPS


# SOUTH_MIGRATION_MODULES = {
#    'taggit': 'taggit.south_migrations',
# }


SWAGGER_SETTINGS = {
    "exclude_namespaces": [],
    "api_version": '0.1',
    "api_path": "/",
    "enabled_methods": [
        'get',
        'post',
        'put',
        'patch',
        'delete'
    ],
    "api_key": '',
    "is_authenticated": False,
    "is_superuser": False,
}

# TINYMCE_JS_URL = 'http://debug.example.org/tiny_mce/tiny_mce_src.js'
PAGE_TINYMCE = True
TINYMCE_DEFAULT_CONFIG = {
    'width': '758px',
    'height': '410px',
    'theme': "advanced",
    'theme_advanced_toolbar_location': "top",
    'theme_advanced_buttons1': "forecolor,italic,bold,justifyleft,justifycenter,justifyright,justifyfull,bullist,numlist,link,formatselect,styleselect,image,code",
    'theme_advanced_buttons2': "",
    'theme_advanced_buttons3': "",
    'inline_styles': True,
    'verify_html': True,
    'relative_urls': False,
    'convert_urls': False,
    'valid_elements': "a[href|target|class],em/i,ul[class],ol,li,h1[class],h2[class],h3[class|id],strong/b,br,p[class|style],img[class|src|alt=|title|width|height|align],table[class],tr[class],td[class|valign|colspan]",
    'content_css': STATIC_URL + "css/tinymce.css," + STATIC_URL + "css/email.css",
    'theme_advanced_blockformats': "p,h1,h2",
    'theme_advanced_resizing': 'true',
    'style_formats': [
        {"title": 'Title', 'block': 'h2', "classes": 'TinyMCE TinyMCETitle'},
        {"title": 'Body', 'block': 'p', "classes": 'TinyMCE TinyMCEBody'},
        {"title": 'Smaller Body', 'block': 'p', "classes": 'TinyMCE TinyMCESmallerBody'},
        {"title": 'Small Text', 'block': 'p', "classes": 'TinyMCE TinyMCESmall'},
        {"title": 'Small Italics', 'block': 'p', "classes": 'TinyMCE TinyMCESmallItalics'},
        {"title": 'Email button', 'selector': 'a', "classes": 'email-button'},
        {"title": 'Email dark row', 'selector': 'tr', "classes": 'email-dark_row'},
        {"title": 'Email header row', 'selector': 'tr', "classes": 'email-header'},
        {"title": 'Email footer row', 'selector': 'tr', "classes": 'email-footer'},
        {"title": 'Email content', 'selector': 'td', "classes": 'email-content'},
        {"title": 'Email button cell', 'selector': 'td', "classes": 'email-button_td'},
        {"title": 'Email small line height', 'block': 'p', "classes": 'email-smalllh'},
    ],
}
TINYMCE_SPELLCHECKER = False
TINYMCE_COMPRESSOR = False
TINYMCE_FILEBROWSER = True

PAGE_TAGGING = True

FILEBROWSER_URL_FILEBROWSER_MEDIA = STATIC_URL + 'filebrowser/'
FILEBROWSER_PATH_FILEBROWSER_MEDIA = MEDIA_ROOT + 'filebrowser/'
FILEBROWSER_STATIC_URL = STATIC_URL + 'filebrowser/'

FILEBROWSER_EXTENSIONS = {
    'Folder': [''],
    'Image': ['.jpg', '.jpeg', '.gif', '.png'],
}
FILEBROWSER_VERSIONS_BASEDIR = '.thumbnails'
FILEBROWSER_URL_TINYMCE = STATIC_URL + "tiny_mce/"
FILEBROWSER_PATH_TINYMCE = STATIC_URL + "tiny_mce/"

FILEBROWSER_VERSIONS = {
    'admin_thumbnail': {'verbose_name': 'Admin Thumbnail', 'width': 60, 'height': 60, 'opts': 'crop'},
}
FILEBROWSER_ADMIN_VERSIONS = []
FILEBROWSER_ADMIN_THUMBNAIL = 'admin_thumbnail'

AUTHENTICATION_BACKENDS = [
    'r2d2.accounts.auth_backends.Emailbackend',
    'django.contrib.auth.backends.ModelBackend',
    'django_su.backends.SuBackend',
]

AUTH_USER_MODEL = "accounts.Account"
MIN_PASSWORD_LENGTH = 8

ALLOWED_HOSTS = [
    '.hello-sales.com',
    '.elasticbeanstalk.com'
]
EC2_PRIVATE_IP = None
try:
    EC2_PRIVATE_IP = requests.get('http://169.254.169.254/latest/meta-data/local-ipv4', timeout = 0.01).text
except requests.exceptions.RequestException:
    pass

if EC2_PRIVATE_IP:
    ALLOWED_HOSTS.append(EC2_PRIVATE_IP)


SITE_ID = 1
SITE_NAME = 'r2d2'
GRAPPELLI_ADMIN_TITLE = SITE_NAME

LOGIN_URL = "/login/"
LOGIN_REDIRECT_URL = "/"
LOGIN_REDIRECT_URLNAME = "index"
LOGOUT_REDIRECT_URLNAME = "login"
SU_LOGIN_REDIRECT_URL = '/login-admin/'
SU_LOGOUT_REDIRECT_URL = '/'

ADMIN_MEDIA_ROOT = location(os.path.join("static", "admin"))

TEMPLATE_DIRS = (
    location("templates"),
)

# SOUTH_TESTS_MIGRATE = False

USE_TZ = True

USE_THOUSAND_SEPARATOR = True

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.memcached.MemcachedCache',
        'LOCATION': '127.0.0.1:11211',
    }
}

COMPRESS_CSS_HASHING_METHOD = 'content'
COMPRESS_OFFLINE = True


COMPRESS_PRECOMPILERS = (
    ('text/x-scss', 'sass --scss --compass {infile} {outfile}'),
)

PASSWORD_MIN_LENGTH = 8
PASSWORD_COMPLEXITY = {"LOWER": 1, "DIGITS": 1}

REST_FRAMEWORK = {
    # Use hyperlinked styles by default.
    # Only used if the `serializer_class` attribute is not set on a view.
    'DEFAULT_MODEL_SERIALIZER_CLASS': 'rest_framework.serializers.HyperlinkedModelSerializer',
    # Use Django's standard `django.contrib.auth` permissions,
    # or allow read-only access for unauthenticated users.
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated'
    ],
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'r2d2.accounts.authentication.TokenAuthentication',
        'r2d2.accounts.authentication.SessionAuthentication',
    ),
    'DEFAULT_FILTER_BACKENDS': ('rest_framework.filters.DjangoFilterBackend',),
    'TEST_REQUEST_RENDERER_CLASSES': (
        'rest_framework.renderers.MultiPartRenderer',
        'rest_framework.renderers.JSONRenderer',
        'rest_framework.renderers.TemplateHTMLRenderer',
    ),
    'DEFAULT_VERSIONING_CLASS': 'rest_framework.versioning.QueryParameterVersioning',
    'DEFAULT_VERSION': 1,
    'PAGE_SIZE': 20,
    'TEST_REQUEST_DEFAULT_FORMAT': 'json'
}

# Celery settings
CELERY_BROKER_URL = ""
CELERY_TASK_ALWAYS_EAGER = False  # whether celery should queue tasks or execute them immediately (for testing)
CELERY_WORKER_POOL_RESTARTS = True
CELERY_TASK_IGNORE_RESULT = True
CELERY_RESULT_BACKEND = None  # or 'rpc://'
CELERY_TASK_EAGER_PROPAGATES = True
CELERY_TASK_CREATE_MISSING_QUEUES = True  # IMPORTANT! unless we manually create our own queues.
CELERY_TASK_DEFAULT_QUEUE = 'default'
CELERY_TASK_DEFAULT_EXCHANGE = 'default'
CELERY_TASK_DEFAULT_EXCHANGE_TYPE = 'direct'  # Can do smart higher/lower level queuing with different types

EMAIL_BACKEND = 'djcelery_email.backends.CeleryEmailBackend'

GOOGLE_TAG_MANAGER = ''

AWS_ACCESS_KEY_ID = 'AKIAJBHLUW7GIEDLQXGQ'
AWS_SECRET_ACCESS_KEY = '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'
#AWS_STORAGE_BUCKET_NAME = 'r2d2-dev-arabella'
AWS_STORAGE_BUCKET_NAME = 'files-dev.hello-sales.com'
AWS_QUERYSTRING_AUTH = False
DEFAULT_FILE_STORAGE = 'r2d2.utils.storage.S3BotoStorageFixed'

# Max # of times the importer will retry a channel API call before giving up for that call
MAX_DATA_IMPORTER_RETRIES = 10

# Min retry time for first rate limited retry, in seconds
MIN_RATE_LIMIT_RETRY_TIME = 60*60

# Min time before rate limit monitor will check to reset the rate limit
RATE_LIMIT_QUEUE_CHECK_COUNTDOWN = 2 * MIN_RATE_LIMIT_RETRY_TIME

# Global remote API rate limit, in case our code begins to rate limit error without being caught (/sec)
DEFAULT_CHANNEL_API_RATE_LIMIT = 2

# Shopify
SHOPIFY_API_KEY = '9701bcb247e85adcb062a0b210d5f1cb'
SHOPIFY_API_SECRET = 'f8070f057e7bcc15a64a881d07d5b3f8'
# SHOPIFY_SCOPES = ['read_content', 'read_themes', 'read_products', 'read_customers', 'read_orders',
#                  'read_script_tags', 'read_fulfillments', 'read_shipping']
# other possible scopes:
# write_themes, write_products, write_customers, write_orders, write_script_tags, write_fulfillments, write_shipping
SHOPIFY_SCOPES = ['read_orders']
SHOPIFY_CALLBACK_ENDPOINT = '/shopify/auth/callback'
SHOPIFY_RATE_LIMIT = 2  # Number of calls allowed per second.  See https://help.shopify.com/api/getting-started/api-call-limit

# Etsy
# matt's keys
ETSY_API_KEY = "7gw45bcpljnujp2wlfe6398b"
ETSY_API_SECRET = "zpruv2b1cs"
# ETSY_API_KEY = 'a4elzoo928uftgjb8vgk3ej0'
# ETSY_API_SECRET = 'hifylh7a8o'
ETSY_SCOPE = 'transactions_r'
# other possible scopes. Multiple scopes should be separated with spaces
# 'listings_w', 'listings_d', 'transactions_w', 'profile_w', 'address_w', 'favorites_rw', 'shops_rw', 'cart_rw',
# 'recommend_rw', 'feedback_r', 'treasury_r', 'treasury_w'
ETSY_CALLBACK_ENDPOINT = '/etsy/auth/callback'
ETSY_RATE_LIMIT = 10  # Number of calls allowed per second.  See https://www.etsy.com/developers/documentation/getting_started/api_basics#section_rate_limiting 

# Square
SQUAREUP_API_KEY = 'fQa48ZcUHUUNZR542VGfxg'
SQUAREUP_API_SECRET = 'dwt11ZGm1cxSb1Kk94JprNSbInsFUfupOEdz3bwnAEs'
SQUAREUP_BASE_URL = 'https://connect.squareup.com/'
SQUAREUP_SCOPE = "PAYMENTS_READ"
SQUAREUP_AUTHORIZATION_ENDPOINT = SQUAREUP_BASE_URL + 'oauth2/authorize?client_id=%(client_id)s&scope=%(scope)s'
SQUAREUP_ACCESS_TOKEN_ENDPOINT = SQUAREUP_BASE_URL + 'oauth2/token'
SQUAREUP_RENEW_TOKEN_ENDPOINT = SQUAREUP_BASE_URL + 'oauth2/clients/%s/access-token/renew'
SQUAREUP_RATE_LIMIT = None  # No explicit rate limit
SQUAREUP_HIGH_VOLUME_LEVEL = 1000  # mean # transactions/day
SQUAREUP_HIGH_UPDATE_TIMEFRAME = 45  # Days to go back to look for transaction updates
SQUAREUP_MEDIUM_VOLUME_LEVEL = 500  # mean # transactions/day
SQUAREUP_MEDIUM_UPDATE_TIMEFRAME = 60  # Days to go back to look for transaction updates
SQUAREUP_LOW_VOLUME_LEVEL = 250  # mean # transactions/day
SQUAREUP_LOW_UPDATE_TIMEFRAME = 90  # Days to go back to look for transaction updates
SQUAREUP_DEFAULT_UPDATE_TIMEFRAME = 180  # Days to go back to look for transaction updates

# Stripe
STRIPE_API_KEY = 'sk_test_NHzDG8LysdhmJq3o6cGNyHSG'
STRIPE_CLIENT_ID = 'ca_A76NdvjLvYuqRLgpsgAJyhBPYH7LXSFC'
STRIPE_BASE_URL = 'https://connect.stripe.com/'
STRIPE_SCOPE = 'read_only'
STRIPE_RESPONSE_TYPE = 'code'
STRIPE_CALLBACK_ENDPOINT = '/stripe/auth/callback?'
STRIPE_AUTHORIZATION_ENDPOINT = STRIPE_BASE_URL + 'oauth/authorize'
STRIPE_ACCESS_TOKEN_ENDPOINT = STRIPE_BASE_URL + 'oauth/token'
STRIPE_RATE_LIMIT = None  # No explicit rate limit

DJANGO_MONEY_RATES = {
    'DEFAULT_BACKEND': 'djmoney_rates.backends.CurrencyLayerBackend',
    'CURRENCYLAYER_KEY': '601a320b8b2e70e3cba08579d74c2095'
}

# here you can put settigns that can be edited through panel
CONSTANCE_CONFIG = {
    'CLIENT_DOMAIN': ('localhost:3000', 'client domain'),
    'ALERTS_RECEIVERS': ('systemalerts@hello-sales.com', 'receivers of alerts - comma separated list')
}
CONSTANCE_BACKEND = 'constance.backends.database.DatabaseBackend'

TESTING = ('test' in sys.argv or 'jenkins' in sys.argv)
TEST_CHARSET = 'utf8'
PEP8_RCFILE = 'pep8.rc'

FAKE_EMAIL_TO = 'fake-mail@hello-sales.com'

if TESTING:
    from testing import *
    update_settings_for_tests(locals())
