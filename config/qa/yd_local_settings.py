# -*- coding: utf-8 -*-
import os

project = lambda: os.path.dirname(os.path.realpath(__file__))
location = lambda x: os.path.join(str(project()), str(x))

PROJECT_ROOT = os.path.abspath(os.path.dirname(__file__))

ADMINS = (
    ('Team', 'systemalerts@hello-sales.com'),
)

MANAGERS = ADMINS

DATABASES = {
    'default': {
        'ENGINE': 'transaction_hooks.backends.mysql',
        'NAME': 'r2d2-qa',
        'USER': 'r2d2',
        'PASSWORD': 'TeldakAfHorpoffyiphbitextiekGockTyhutJenreyltajiar',
        'HOST': 'ydqadb.ydtech.co',
        'PORT': '3306',
        'ATOMIC_REQUESTS': True
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
BROKER_URL = 'librabbitmq://r2d2-api-qa:r2d2-api-qa@localhost:5672/r2d2-api-qa'

AWS_ACCESS_KEY_ID = 'AKIAJMICFR3WHFTZLG4A'
AWS_SECRET_ACCESS_KEY = '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'
AWS_STORAGE_BUCKET_NAME = 'r2d2-qa-arabella'

SQUAREUP_API_KEY = 'sq0idp-XK_5K4LY55FBbUQcpqLtRw'
SQUAREUP_API_SECRET = 'sq0csp-xSFx5gcCvqavEJsJx2m0E1vh0rdupk6MhcK9_8a2Smw'

CONSTANCE_CONFIG = {
    'CLIENT_DOMAIN': ('r2d2-qa.arabel.la', 'client domain'),
    'ALERTS_RECEIVERS': ('systemalerts@hello-sales.com', 'receivers of alerts - comma separated list')
}

RAVEN_CONFIG = {
}
