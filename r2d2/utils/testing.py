import unittest

from django.conf import settings

skipUnlessMySQL = unittest.skipIf(
    settings.DATABASES['default']['ENGINE'] !=
    'django.db.backends.mysql',
    "This test uses MySQL specific features.")
