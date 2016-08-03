# -*- coding: utf-8 -*-
import os

project = lambda: os.path.dirname(os.path.realpath(__file__))
location = lambda x: os.path.join(str(project()), str(x))

PROJECT_ROOT = os.path.abspath(os.path.dirname(__file__))

ADMINS = (
    ('Team', 'team@ydtech.co'),
)

MANAGERS = ADMINS

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'api-hello-sales',
        'USER': 'api-hello-sales',
        'PASSWORD': 'MenUtheewajFugAisBochainOlmAmt',
        'HOST': 'ydproddb.cisjmnb7cksz.us-east-1.rds.amazonaws.com',
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

# TODO: create app for r2d2 production
SQUAREUP_API_KEY = 'p4OiJb_Aa9527UGzFbFz4g'
SQUAREUP_API_SECRET = 'tBWttX7fCBcphFF7JUkoeHt-JSKkmZ9J_Qc-w6K8yhY'

CONSTANCE_CONFIG = {
    'CLIENT_DOMAIN': ('hello-sales.com', 'client domain'),
    'ALERTS_RECEIVERS': ('team@ydtech.co', 'receivers of alerts - comma separated list')
}

import raven

RAVEN_CONFIG = {
    'dsn': 'https://97293106f2a543859de54e596489f320:7a544014f02644f289d2353dc452f2bb@sentry.arabel.la/17',
    'private_dsn': 'https://97293106f2a543859de54e596489f320@sentry.arabel.la/17',
}
