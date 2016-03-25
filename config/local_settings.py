# -*- coding: utf-8 -*-
DEBUG = True
SASS_DEBUG = DEBUG
TEMPLATE_DEBUG = DEBUG
# COMPRESS_ENABLED = True
ADMINS = ()

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'XXX',
        'USER': 'XXX',
        'PASSWORD': 'XXX',
        'HOST': 'localhost',
        'PORT': '3306',
    },
}

MONGODB_DATABASES = {
    'mongo': {
        'name': '',
        'username': '',
        'password': '',
        'host': 'localhost',
        'port': 27017,
    }
}

INTERNAL_IPS = (
    "127.0.0.1",
)

if SASS_DEBUG:
    COMPRESS_PRECOMPILERS = (
        # ('text/x-scss', 'sass --scss  --debug-info {infile} {outfile}'),
        ('text/x-scss', 'sass --scss --compass  --debug-info {infile} {outfile}'),
    )
else:
    COMPRESS_PRECOMPILERS = (
        ('text/x-scss', 'sass --scss --compass {infile} {outfile}'),
    )
