# -*- coding: utf-8 -*-
import os

IS_SECURE = True

project = lambda: os.path.dirname(os.path.realpath(__file__))
location = lambda x: os.path.join(str(project()), str(x))

PROJECT_ROOT = os.path.abspath(os.path.dirname(__file__))

EMAIL_USE_TLS = True
EMAIL_HOST = 'email-smtp.us-east-1.amazonaws.com'
EMAIL_HOST_PASSWORD = 'AhhBbt76BJLFSky4xbZ3RNt0KRntU8FnHAuCxHdeJ7RG'
EMAIL_HOST_USER = 'AKIAJKORSLH4UBCGMXVQ'
EMAIL_PORT = 587
DEFAULT_FROM_EMAIL = '"HelloSales" <hello@hello-sales.com>'

DEBUG = False
ENV_PREFIX = 'api-hello-sales'

ADMINS = (
    ('Matt Laszuk', 'matt.laszuk@gmail.com')
)

MANAGERS = ADMINS

DATABASES = {
    'default': {
        'ENGINE': 'transaction_hooks.backends.mysql',
        'NAME': 'hello_sales',
        'USER': 'hello',
        'PASSWORD': 'GxKGVmbGwh3MtRAMwASx',
        'HOST': 'hello-sales-prod.cmhvzu4rd3w9.us-east-1.rds.amazonaws.com',
        'PORT': '3306',
        'ATOMIC_REQUESTS': True
    },
}

MONGODB_DATABASES = {
    'default': {
        'name': 'mongodb-prod',
        'username': 'db',
        'password': 'BzUatHShXTFN9qyfHFnX',
        'host': '10.0.63.200',
        'port': 25140,
    }
}

AWS_STORAGE_BUCKET_NAME = 'files.hello-sales.com'

SECRET_KEY = 'prodvay&e&9hdwo_bniq-$z0j64q4w27-fm58nu9!m+i$nc0e!*!o0'

CELERY_ALWAYS_EAGER = False
BROKER_URL = 'librabbitmq://api-hello-sales:iydocuwjp9xt@10.0.63.202:5672/api-hello-sales'

SHOPIFY_API_KEY = '74ce0b5cb25ebb2fde10ba55fcf24cbc'
SHOPIFY_API_SECRET = '9b6bd9a8ac0b7a7803fa735de0196989'

SQUAREUP_API_KEY = 'sq0idp-bOxK1iCqtPUHmobFsqSsVg'
SQUAREUP_API_SECRET = 'sq0csp-3ZxZ0wxmKVlPICcp6lU_XoUzWpbIuWgwiyPVGC362vU'

CONSTANCE_CONFIG = {
    'CLIENT_DOMAIN': ('hello-sales.com', 'client domain'),
    'ALERTS_RECEIVERS': ('matt.laszuk@gmail.com', 'receivers of alerts - comma separated list')
}

RAVEN_CONFIG = {
    'dsn': 'https://0403f307016d4e69b5413f4d43689a26:b28b724d07c440889434553055d2f740@sentry.io/153766'
}

# Local memcache setting.
# CACHES = {
#    'default': {
#        'BACKEND': 'django.core.cache.backends.memcached.MemcachedCache',
#        'LOCATION': '127.0.0.1:11211',
#        }
# }
