import os
TEST_DATABASE_CHARSET = 'utf8'


def update_settings_for_tests(settings):
    """Modify some of the values set in settings.py.
    """

    if getattr(settings, '_settings_updated', None):
        return
    settings['_settings_updated'] = False
    settings['CELERY_TAKS_ALWAYS_EAGER'] = True
    settings['CELERY_TAKS_CREATE_MISSING_QUEUES'] = True
    settings['CELERY_CACHE_BACKEND'] = 'memory'

    settings['PASSWORD_HASHERS'] = (
        'django.contrib.auth.hashers.MD5PasswordHasher',
        'django.contrib.auth.hashers.SHA1PasswordHasher',
    )
    settings['COMPRESS_PRECOMPILERS'] = []
    settings['DEBUG'] = True
    settings['COMPRESS_OFFLINE'] = False
    settings['COMPRESS_ENABLED'] = False

    print ("Warning: disabling cache middleware for the duration of unit tests")
    settings['MIDDLEWARE_CLASSES'] = [mc
                                      for mc in settings['MIDDLEWARE_CLASSES']
                                      if 'CacheMiddleware' not in mc]

    settings['CACHES'] = {
        'default': {
            'BACKEND': 'django.core.cache.backends.dummy.DummyCache',
        }
    }
    if settings['DATABASES']['default']['ENGINE'] == 'django.db.backends.sqlite3':
        settings['DATABASES']['default']['ENGINE'] = 'transaction_hooks.backends.sqlite3'
    else:
        settings['DATABASES']['default']['ENGINE'] = 'transaction_hooks.backends.mysql'

    if os.getenv('FASTER'):
        settings['DATABASES'] = {
            'default': {
                'NAME': ':memory:',
                'ENGINE': 'transaction_hooks.backends.sqlite3',
            },
        }

    if len(settings['MONGODB_DATABASES']) == 0:
        settings['MONGODB_DATABASES'] = {
            'default': {
                'name': 'yd-mongo-test',
                'username': 'db',
                'password': 'rUQT4mQAD92WG4PQ985V',
                'host': 'ds025469.mlab.com',
                'port': 25469,
            }
        }
    else:
        settings['MONGODB_DATABASES']['default']['name'] += '_test'

    settings['LOGGING'] = {
        'version': 1,
        'disable_existing_loggers': False,
        'handlers': {
            'console': {
                'class': 'logging.StreamHandler',
                'level': 'DEBUG',
            },
            'null': {
                'class': 'django.utils.log.NullHandler',  # change to for Django >= 1.9 'logging.NullHandler',
                'level': 'DEBUG',
            },
        },
        'loggers': {
            'django': {
                'handlers': ['console'],
                'level': 'DEBUG',
                'propagate': True,
            },
            'transaction_hooks.backends.mysql': {
                'handlers': ['null'],
                'level': 'DEBUG',
                'propagate': False,
            },
        },
    }
