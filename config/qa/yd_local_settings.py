# -*- coding: utf-8 -*-
import os

PROJECT_ROOT = os.path.abspath(os.path.dirname(__file__))

ADMINS = (
    ('YD', 'team@arabel.la'),
)

MANAGERS = ADMINS

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'r2d2-qa',
        'USER': 'r2d2',
        'PASSWORD': '',
        'HOST': 'ydproddb.cisjmnb7cksz.us-east-1.rds.amazonaws.com',
        'PORT': '3306',
    },
}

DEBUG = False

SECRET_KEY = 'qavay&e&9hdwo_bniq-$z0j64q4w27-fm58nu9!m+i$nc0e!*!o0'

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

ENV_PREFIX = 'r2d2-qa'

CELERY_ALWAYS_EAGER = False
# BROKER_URL = 'librabbitmq://r2d2_qa:jfyhhgckginv@localhost:5672/r2d2_qa'

AWS_STORAGE_BUCKET_NAME = 'r2d2-dev'
