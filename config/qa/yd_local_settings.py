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
        'NAME': 'r2d2-qa',
        'USER': 'r2d2',
        'PASSWORD': 'TeldakAfHorpoffyiphbitextiekGockTyhutJenreyltajiar',
        'HOST': 'yddevdb.ydtech.co',
        'PORT': '3306',
    },
}

MONGODB_DATABASES = {
    'default': {
        'name': 'yd-mongodb-qa',
        'username': 'db',
        'password': '6RFMCCpNYhhVZdXTeQj2',
        'host': 'ds025439.mlab.com',
        'port': 25439,
    }
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
BROKER_URL = 'librabbitmq://r2d2_qa:jfyhhgckginv@localhost:5672/r2d2_qa'

AWS_ACCESS_KEY_ID = 'AKIAJBZGHE4FDR5M4ROQ'
AWS_SECRET_ACCESS_KEY = 'af1myj+5KEmZSSYznC3MBhS9N4PLJp030myjdT8'
AWS_STORAGE_BUCKET_NAME = 'r2d2-qa-arabella'

# TODO: create app for r2d2 qa
SQUAREUP_API_KEY = 'p4OiJb_Aa9527UGzFbFz4g'
SQUAREUP_API_SECRET = 'tBWttX7fCBcphFF7JUkoeHt-JSKkmZ9J_Qc-w6K8yhY'

CONSTANCE_CONFIG = {
    'CLIENT_DOMAIN': ('r2d2-qa.arabel.la', 'client domain')
}

import raven

RAVEN_CONFIG = {
    'dsn': 'https://97293106f2a543859de54e596489f320:7a544014f02644f289d2353dc452f2bb@sentry.arabel.la/7',
    'private_dsn': 'https://97293106f2a543859de54e596489f320@sentry.arabel.la/7',
}
