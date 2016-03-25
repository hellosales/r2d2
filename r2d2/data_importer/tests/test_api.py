from django.test import TestCase

from r2d2.data_importer.api import DataImporter


class DataImporterApiTestCase(TestCase):
    """ test if registering models work """

    def test_registering_models(self):
        """ simple checks registered models
            please add here models when a new data importer API is added"""

        registered_models = DataImporter.list_registered()
        self.assertIn('EtsyAccount', registered_models)
        self.assertIn('SquareupAccount', registered_models)
        self.assertIn('ShopifyStore', registered_models)
