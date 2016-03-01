# -*- coding: utf-8 -*-
import os

DEBUG = False
SASS_DEBUG = DEBUG
TEMPLATE_DEBUG = False
PROJECT_ROOT = os.path.abspath(os.path.dirname(__file__))

ADMINS = (
    ('YD', 'team@arabel.la'),
)

MANAGERS = ADMINS

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'r2d2-dev',
        'USER': 'r2d2',
        'PASSWORD': '',
        'HOST': 'yddevdb.ydtech.co',
        'PORT': '3306',
    },
}

SECRET_KEY = 'devvay&e&9hdwo_bniq-$z0j64q4w27-fm58nu9!m+i$nc0e!*!o0'

# Local memcache setting.
# CACHES = {
#    'default': {
#        'BACKEND': 'django.core.cache.backends.memcached.MemcachedCache',
#        'LOCATION': '127.0.0.1:11211',
#        }
# }

RAVEN_CONFIG = {
    'dsn': '',
}

# Do not compress on dev
COMPRESS_JS_FILTERS = []

ENV_PREFIX = 'r2d2-dev'

#BROKER_URL = 'librabbitmq://r2d2_dev:iydocuwjp9xt@localhost:5672/r2d2_dev'
CELERY_ALWAYS_EAGER = False


AWS_STORAGE_BUCKET_NAME = 'r2d2-dev'
