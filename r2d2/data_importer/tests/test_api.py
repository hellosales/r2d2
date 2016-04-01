import mock

from r2d2.data_importer.api import DataImporter
from r2d2.shopify_api.models import ShopifyStore
from r2d2.utils.test_utils import APIBaseTestCase


class DataImporterApiTestCase(APIBaseTestCase):
    """ test if registering models work """
    def test_registering_models(self):
        """ simple checks registered models
            please add here models when a new data importer API is added"""

        registered_models = DataImporter.list_registered()
        self.assertIn('EtsyAccount', registered_models)
        self.assertIn('SquareupAccount', registered_models)
        self.assertIn('ShopifyStore', registered_models)

    def test_importer_flow(self):
        """ checks the whole importer flow """
        self._create_user()
        account = ShopifyStore.objects.create(user=self.user, access_token='token', name='name')
        not_authorized_account = ShopifyStore.objects.create(user=self.user, access_token='token', name='other-name')

        with mock.patch('r2d2.data_importer.tasks.fetch_data_task.apply_async') as mocked_find:
            mocked_find.return_value = None

            # run importer
            DataImporter.run_fetching_data()

            # TODO: mock - count

            # check status #1
            self.assertEqual(ShopifyStore.objects.get(id=account.id).fetch_status, ShopifyStore.FETCH_SUCCESS)

            # check status #2
            self.assertEqual(ShopifyStore.objects.get(id=not_authorized_account.id).fetch_status,
                             ShopifyStore.FETCH_IDLE)
