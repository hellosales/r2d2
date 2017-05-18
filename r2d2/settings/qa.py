from defaults import *

DEBUG = False

LOGGING['handlers']['applogfile']['filename'] = '/var/log/r2d2/r2d2.log'

DEFAULT_FROM_EMAIL = '"QA - HelloSales" <hello-qa@hello-sales.com>'

AWS_STORAGE_BUCKET_NAME = 'files-qa.hello.sales'
MEDIA_URL = 'https://%s.s3.amazonaws.com/' % AWS_STORAGE_BUCKET_NAME


SECRET_KEY = 'qavay&e&9hdwo_bniq-$z0j64q4w27-fm58nu9!m+i$nc0e!*!o0'

RAVEN_CONFIG = {
    'dsn': 'https://97293106f2a543859de54e596489f320:7a544014f02644f289d2353dc452f2bb@sentry.arabel.la/7',
    'private_dsn': 'https://97293106f2a543859de54e596489f320@sentry.arabel.la/7',
}

ENV_PREFIX = 'r2d2-qa'

CELERY_TASK_ALWAYS_EAGER = False  # whether celery should queue tasks or execute them immediately (for testing)
CELERY_BROKER_URL = 'librabbitmq://r2d2-api-qa:r2d2-api-qa@localhost:5672/r2d2-api-qa'

SQUAREUP_API_KEY = 'sq0idp-XK_5K4LY55FBbUQcpqLtRw'
SQUAREUP_API_SECRET = 'sq0csp-xSFx5gcCvqavEJsJx2m0E1vh0rdupk6MhcK9_8a2Smw'

CONSTANCE_CONFIG = {
    'CLIENT_DOMAIN': ('r2d2-qa.arabel.la', 'client domain'),
    'ALERTS_RECEIVERS': ('team@ydtech.co', 'receivers of alerts - comma separated list')
}
