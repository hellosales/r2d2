from defaults import *

DEBUG = False

ENV_PREFIX = 'api-hello-sales'

LOGGING['handlers']['applogfile']['filename'] = '/var/log/r2d2/r2d2.log'

DEFAULT_FROM_EMAIL = '"HelloSales" <hello@hello-sales.com>'

AWS_STORAGE_BUCKET_NAME = 'files.hello-sales.com'
MEDIA_URL = 'https://%s.s3.amazonaws.com/' % AWS_STORAGE_BUCKET_NAME

SECRET_KEY = 'prodvay&e&9hdwo_bniq-$z0j64q4w27-fm58nu9!m+i$nc0e!*!o0'

CELERY_TASK_ALWAYS_EAGER = False  # whether celery should queue tasks or execute them immediately (for testing)
CELERY_BROKER_URL = 'librabbitmq://api-hello-sales:iydocuwjp9xt@10.0.63.202:5672/api-hello-sales'

SHOPIFY_API_KEY = '74ce0b5cb25ebb2fde10ba55fcf24cbc'
SHOPIFY_API_SECRET = '9b6bd9a8ac0b7a7803fa735de0196989'

SQUAREUP_API_KEY = 'sq0idp-bOxK1iCqtPUHmobFsqSsVg'
SQUAREUP_API_SECRET = 'sq0csp-3ZxZ0wxmKVlPICcp6lU_XoUzWpbIuWgwiyPVGC362vU'

STRIPE_API_KEY = 'sk_live_ifufH5vjeCCodNsjg6Fhhrie'

CONSTANCE_CONFIG = {
    'CLIENT_DOMAIN': ('hello-sales.com', 'client domain'),
    'ALERTS_RECEIVERS': ('matt.laszuk@gmail.com', 'receivers of alerts - comma separated list')
}

RAVEN_CONFIG = {
    'dsn': 'https://0403f307016d4e69b5413f4d43689a26:b28b724d07c440889434553055d2f740@sentry.io/153766'
}

SWAGGER_SETTINGS["is_authenticated"] = True,  # Set to True to enforce user authentication,
SWAGGER_SETTINGS["is_superuser"] = True,  # Set to True to enforce admin only access
REST_FRAMEWORK['DEFAULT_RENDERER_CLASSES'] = ['rest_framework.renderers.JSONRenderer']
