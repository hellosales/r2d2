# -*- coding: utf-8 -*-
import os

IS_SECURE = True

project = lambda: os.path.dirname(os.path.realpath(__file__))
location = lambda x: os.path.join(str(project()), str(x))

PROJECT_ROOT = os.path.abspath(os.path.dirname(__file__))

EMAIL_USE_TLS = True  # fixme
EMAIL_HOST = 'smtp.sendgrid.net'  # fixme
EMAIL_HOST_PASSWORD = "edIdtatecyecThaxorrijkiQuotEb0"  # fixme
EMAIL_HOST_USER = 'hello-sales'  # fixme
EMAIL_PORT = 587  # fixme
DEFAULT_FROM_EMAIL = '"HelloSales" <hello@hello-sales.com>'

ADMINS = (
    ('Team', 'team@ydtech.co'),
    ('Matt Laszuk', 'matt.laszuk@gmail.com'),
)

MANAGERS = ADMINS

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'api-hello-sales',
        'USER': 'api-hello-sales',
        'PASSWORD': 'MenUtheewajFugAisBochainOlmAmt',
        'HOST': 'ydproddb.ydtech.co',
        'PORT': '3306',
        'ATOMIC_REQUESTS': True
    },
}

MONGODB_DATABASES = {
    'default': {
        'name': 'yd-mongodb-prod',
        'username': 'db',
        'password': 'BzUatHShXTFN9qyfHFnX',
        'host': 'ds025389.mlab.com',
        'port': 25389,
    }
}

DEBUG = False

SECRET_KEY = 'prodvay&e&9hdwo_bniq-$z0j64q4w27-fm58nu9!m+i$nc0e!*!o0'

# Local memcache setting.
# CACHES = {
#    'default': {
#        'BACKEND': 'django.core.cache.backends.memcached.MemcachedCache',
#        'LOCATION': '127.0.0.1:11211',
#        }
# }


ENV_PREFIX = 'api-hello-sales'

CELERY_ALWAYS_EAGER = False
BROKER_URL = 'librabbitmq://api-hello-sales:iydocuwjp9xt@localhost:5672/api-hello-sales'

AWS_STORAGE_BUCKET_NAME = 'api-hello-sales'

# IAM Role
AWS_ACCESS_KEY_ID = 'AKIAITSHDBMHBTIKBTXQ'
AWS_SECRET_ACCESS_KEY = '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'

SHOPIFY_API_KEY = '74ce0b5cb25ebb2fde10ba55fcf24cbc'
SHOPIFY_API_SECRET = '9b6bd9a8ac0b7a7803fa735de0196989'

SQUAREUP_API_KEY = 'sq0idp-bOxK1iCqtPUHmobFsqSsVg'
SQUAREUP_API_SECRET = 'sq0csp-3ZxZ0wxmKVlPICcp6lU_XoUzWpbIuWgwiyPVGC362vU'

CONSTANCE_CONFIG = {
    'CLIENT_DOMAIN': ('hello-sales.com', 'client domain'),
    'ALERTS_RECEIVERS': ('team@ydtech.co,matt.laszuk@gmail.com', 'receivers of alerts - comma separated list')
}

import raven

RAVEN_CONFIG = {
    'dsn': 'https://97293106f2a543859de54e596489f320:7a544014f02644f289d2353dc452f2bb@sentry.arabel.la/17',
    'private_dsn': 'https://97293106f2a543859de54e596489f320@sentry.arabel.la/17',
}
