# -*- coding: utf-8 -*-
import os

project = lambda: os.path.dirname(os.path.realpath(__file__))
location = lambda x: os.path.join(str(project()), str(x))

DEBUG = False
SASS_DEBUG = DEBUG
TEMPLATE_DEBUG = False
PROJECT_ROOT = os.path.abspath(os.path.dirname(__file__))

ADMINS = (
    ('Team', 'team@ydtech.co'),
)

MANAGERS = ADMINS

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'r2d2-dev',
        'USER': 'r2d2',
        'PASSWORD': 'TeldakAfHorpoffyiphbitextiekGockTyhutJenreyltajiar',
        'HOST': 'yddevdb.ydtech.co',
        'PORT': '3306',
        'ATOMIC_REQUESTS': True
    },
}

MONGODB_DATABASES = {
    'default': {
        'name': 'yd-mongodb-dev',
        'username': 'db',
        'password': 'q73nRh3uXJJpacjuFPwa',
        'host': 'ds021999.mlab.com',
        'port': 21999,
    }
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

BROKER_URL = 'librabbitmq://r2d2_dev:iydocuwjp9xt@localhost:5672/r2d2_dev'
CELERY_ALWAYS_EAGER = False

AWS_ACCESS_KEY_ID = 'AKIAJBHLUW7GIEDLQXGQ'
AWS_SECRET_ACCESS_KEY = '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'
AWS_STORAGE_BUCKET_NAME = 'r2d2-dev-arabella'

SQUAREUP_API_KEY = 'sq0idp-Y7WFLOjMPp11LYNp76_4_A'
SQUAREUP_API_SECRET = 'sq0csp-WnMisBjD0DtEoYeM0ZK7Bi1_cYb0V5oRCN2djDcYAC0'

CONSTANCE_CONFIG = {
    'CLIENT_DOMAIN': ('r2d2-dev.arabel.la', 'client domain')
}

import raven

RAVEN_CONFIG = {
    'dsn': 'https://97293106f2a543859de54e596489f320:7a544014f02644f289d2353dc452f2bb@sentry.arabel.la/7',
    'private_dsn': 'https://97293106f2a543859de54e596489f320@sentry.arabel.la/7',
}
