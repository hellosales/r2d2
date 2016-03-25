# -*- coding: utf-8 -*-
from django.test import TestCase
from django.conf import settings

from mongoengine import connection


class MongoConnectionTest(TestCase):
    """ simple test checking if connection to mongo was registered """

    def test_connections(self):
        """ getting connection server info - if connection is not established it will throw an error """
        self.assertTrue(hasattr(settings, 'MONGODB_DATABASES'))
        self.assertGreater(len(settings.MONGODB_DATABASES.keys()), 0)

        for alias in settings.MONGODB_DATABASES:
            conn = connection.get_connection(alias)
            server_info = conn.server_info()
            self.assertIn('version', server_info)
            self.assertGreater(server_info['version'], '3.0.0')
