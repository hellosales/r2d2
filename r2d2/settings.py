# -*- coding: utf-8 -*-
import os.path

DEBUG = False
TEMPLATE_DEBUG = DEBUG

project = lambda: os.path.dirname(os.path.realpath(__file__))
location = lambda x: os.path.join(str(project()), str(x))

EMAIL_USE_TLS = True
EMAIL_HOST = 'email-smtp.us-east-1.amazonaws.com'
EMAIL_HOST_PASSWORD = 'AoQcpXJ+B4go1BuP8DtB/GYSHn+dBrqYdaQTWJr3CXG+'
EMAIL_HOST_USER = 'AKIAIJQ2QA6WO6UKCYKQ'
EMAIL_PORT = 587
DEFAULT_FROM_EMAIL = '"Arabella No-reply" <no-reply@arabel.la>'

ADMINS = (
    ('Team', 'team@arabel.la'),
)
MANAGERS = ADMINS

DATABASES = {}

FORCE_SCRIPT_NAME = ""

TIME_ZONE = "US/Eastern"

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'en'

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = False

# This is defined here as a do-nothing function because we can't import
# django.utils.translation -- that module depends on the settings.
gettext_noop = lambda s: s

# here is all the languages supported by the CMS
PAGE_LANGUAGES = (
    ('en', gettext_noop('English')),
    # ('es', gettext_noop('Spanish')),
)

PAGE_DEFAULT_TEMPLATE = 'pages/base.html'

PAGE_TEMPLATES = (
    ('pages/base.html', 'base'),
)

PAGE_USE_SITE_ID = True


# If you set this to False, Django will not format dates, numbers and
# calendars according to the current locale
USE_L10N = True

DEFAULT_DATE_FORMAT = '%B %d, %Y'

# Absolute filesystem path to the directory that will hold user-uploaded files.
# Example: "/home/media/media.lawrence.com/media/"
MEDIA_ROOT = location(os.path.join("site_media", "media"))

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash.
# Examples: "http://media.lawrence.com/media/", "http://example.com/media/"
MEDIA_URL = '/media/'

# Absolute path to the directory static files should be collected to.
# Don't put anything in this directory yourself; store your static files
# in apps' "static/" subdirectories and in STATICFILES_DIRS.
# Example: "/home/media/media.lawrence.com/static/"
STATIC_ROOT = location(os.path.join("site_media", "static"))

# Additional directories which hold static files
STATICFILES_DIRS = [
    location("static"),
]

STATICFILES_FINDERS = (
    "django.contrib.staticfiles.finders.FileSystemFinder",
    "django.contrib.staticfiles.finders.AppDirectoriesFinder",
    "compressor.finders.CompressorFinder",
)

# URL prefix for static files.
# Example: "http://media.lawrence.com/static/"
STATIC_URL = "/static/"

# Make this unique, and don't share it with anybody.
SECRET_KEY = 'localvay&e&9hdwo_bniq-$z0j64q4w27-fm58nu9!m+i$nc0e!*!o0'

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.BrokenLinkEmailsMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    # 'django.middleware.doc.XViewMiddleware',
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
    'r2d2.notifications',
    'r2d2.emails',
    'r2d2.utils',
)

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.humanize',
    'basic_cms',
    'compressor',
    'taggit',
    # 'mptt',
    "tinymce",
    'grappelli',
    'filebrowser',
    # 'modeltranslation',
    'django_su',
    'django.contrib.admin',
    'raven.contrib.django.raven_compat',
    'django_jenkins',
    'ydcommon',
    # 'djcelery',
    'rest_framework_swagger',
    'rest_framework',
    'rest_framework.authtoken',
    'templateaddons',
    'sorl.thumbnail',
) + PROJECT_APPS


# SOUTH_MIGRATION_MODULES = {
#    'taggit': 'taggit.south_migrations',
# }


SWAGGER_SETTINGS = {
    "exclude_namespaces": [],  # List URL namespaces to ignore
    "api_version": '0.1',  # Specify your API's version
    "api_path": "/",  # Specify the path to your API not a root level
    "enabled_methods": [  # Specify which methods to enable in Swagger UI
        'get',
        'post',
        'put',
        'patch',
        'delete'
    ],
    "api_key": '',  # An API key
    "is_authenticated": False,  # Set to True to enforce user authentication,
    "is_superuser": False,  # Set to True to enforce admin only access
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
    '.arabel.la',
    '.r2d2.com',
]


SITE_ID = 1

SITE_NAME = 'r2d2'
GRAPPELLI_ADMIN_TITLE = SITE_NAME

LOGIN_URL = "/login/"
LOGIN_REDIRECT_URL = "/"
LOGIN_REDIRECT_URLNAME = "index"
LOGOUT_REDIRECT_URLNAME = "login"
SU_LOGIN_REDIRECT_URL = LOGIN_REDIRECT_URL
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
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
    }
}

COMPRESS_CSS_HASHING_METHOD = 'content'
COMPRESS_OFFLINE = True

ENV_PREFIX = 'r2d2-local'

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
    'PAGE_SIZE': 10,
    'TEST_REQUEST_DEFAULT_FORMAT': 'json'
}
BROKER_URL = ""
CELERY_ALWAYS_EAGER = True
CELERYD_POOL_RESTARTS = True
CELERY_IGNORE_RESULT = True
CELERY_RESULT_BACKEND = 'amqp'
CELERY_EAGER_PROPAGATES_EXCEPTIONS = True

GOOGLE_TAG_MANAGER = ''

AWS_ACCESS_KEY_ID = 'AKIAJ7QEF3AJBXLTJ63A'
AWS_SECRET_ACCESS_KEY = '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'
AWS_STORAGE_BUCKET_NAME = 'r2d2-dev'
AWS_QUERYSTRING_AUTH = False
DEFAULT_FILE_STORAGE = 'r2d2.utils.storage.S3BotoStorageFixed'

try:
    from local_settings import *
except ImportError:
    print ("no local_settings.py file?")

MEDIA_URL = 'https://%s.s3.amazonaws.com/' % AWS_STORAGE_BUCKET_NAME

import sys
TESTING = ('test' in sys.argv or 'jenkins' in sys.argv)
TEST_CHARSET = 'utf8'
PEP8_RCFILE = 'pep8.rc'

if TESTING:
    from test_settings import *
    update_settings_for_tests(locals())

# import djcelery
# djcelery.setup_loader()
