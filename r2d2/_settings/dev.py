from defaults import *


DEBUG = True
SASS_DEBUG = DEBUG
TEMPLATE_DEBUG = DEBUG

DEFAULT_FROM_EMAIL = '"Dev - HelloSales" <hello-dev@hello-sales.com>'

ENV_PREFIX = 'r2d2-dev'

AWS_STORAGE_BUCKET_NAME = 'files-dev.hello-sales.com'
MEDIA_URL = 'https://%s.s3.amazonaws.com/' % AWS_STORAGE_BUCKET_NAME

