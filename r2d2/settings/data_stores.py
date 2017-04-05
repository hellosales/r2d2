import os

if 'RDS_DB_NAME' in os.environ:
    DATABASES = {
        'default': {
            'ENGINE': 'transaction_hooks.backends.mysql',
            'NAME': os.environ['RDS_DB_NAME'],
            'USER': os.environ['RDS_USERNAME'],
            'PASSWORD': os.environ['RDS_PASSWORD'],
            'HOST': os.environ['RDS_HOSTNAME'],
            'PORT': 3306,
            'ATOMIC_REQUESTS': True
        }
    }
else:
    DATABASES = {
        'default': {
            'ENGINE': 'transaction_hooks.backends.mysql',
            'NAME': 'hello_sales',
            'USER': 'hello',
            'PASSWORD': 'sales',
            'HOST': 'localhost',
            'PORT': 3336,
        }
    }


if 'MONGO_NAME' in os.environ:
    DATABASES = {
        'default': {
            'name': os.environ['MONGO_NAME'],
            'username': os.environ['MONGO_USERNAME'],
            'password': os.environ['MONGO_PASSWORD'],
            'host': os.environ['MONGO_HOSTNAME'],
            'port': 27017,
        }
    }
else:
    MONGODB_DATABASES = {
        'default': {
            'name': '',
            'username': '',
            'password': '',
            'host': 'localhost',
            'port': 27017,
        }
    }
