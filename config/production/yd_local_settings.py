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
        'NAME': 'r2d2',
        'USER': 'r2d2',
        'PASSWORD': '',
        'HOST': '',
        'PORT': '3306',
    },
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

RAVEN_CONFIG = {
    'dsn': '',
}

ENV_PREFIX = 'r2d2-prod'

CELERY_ALWAYS_EAGER = False
# BROKER_URL = 'librabbitmq://r2d2_prod:jfyhhgckginv@localhost:5672/r2d2_prod'

AWS_STORAGE_BUCKET_NAME = 'r2d2-'

# IAM Role
AWS_ACCESS_KEY_ID = ''
AWS_SECRET_ACCESS_KEY = ''

import raven

RAVEN_CONFIG = {
    'dsn': 'https://97293106f2a543859de54e596489f320:7a544014f02644f289d2353dc452f2bb@sentry.arabel.la/7',
    'private_dsn': 'https://97293106f2a543859de54e596489f320@sentry.arabel.la/7',
    # If you are using git, you can also automatically configure the
    # release based on the git info.
    'release': raven.fetch_git_sha(os.path.join(str(project()), '..'))
}
