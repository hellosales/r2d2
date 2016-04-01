import mock

from datetime import date
from freezegun import freeze_time

from r2d2.shopify_api.models import ImportedShopifyOrder
from r2d2.shopify_api.models import ShopifyStore
from r2d2.shopify_api.tests.sample_data import SHOPIFY_ORDERS
from r2d2.utils.test_utils import APIBaseTestCase


class TestImport(APIBaseTestCase):
    """ test if importer flow works """

    def setUp(self):
        self._create_user()
        self.account = ShopifyStore.objects.create(user=self.user, access_token='token', name='name')

    def tearDown(self):
        ImportedShopifyOrder.objects.filter(account_id=self.account.id).delete()

    def test_import(self):
        """ test importing data from shopify
            - call fetch_data for the first time - make sure we go with first import path, object is created & data
                of last transaction update is saved
            - call fetch_data for the second time - make sure we go with the update path, object should be updated
                (since the same one will be returned) """

        order_json = SHOPIFY_ORDERS['orders'][0]

        with freeze_time('2016-04-01'):
            with mock.patch('shopify.Order.find') as mocked_find:
                mocked_find.return_value = SHOPIFY_ORDERS['orders']

                self.account.fetch_status = ShopifyStore.FETCH_SCHEDULED
                self.account.fetch_data()
                mocked_find.assert_called_with(status='any', limit=ShopifyStore.MAX_REQUEST_LIMIT)

                self.assertEqual(ImportedShopifyOrder.objects.filter(account_id=self.account.id).count(), 1)
                iso = ImportedShopifyOrder.objects.filter(account_id=self.account.id)[0]
                self.assertEqual(iso.shopify_id, order_json['id'])
                self.assertNotEqual(iso.id.generation_time.date(), date(2014, 8, 25))

                self.account.fetch_status = ShopifyStore.FETCH_SCHEDULED
                self.account.fetch_data()
                mocked_find.assert_called_with(status='any', updated_at_min=iso.updated_at,
                                               limit=ShopifyStore.MAX_REQUEST_LIMIT)

                self.assertEqual(ImportedShopifyOrder.objects.filter(account_id=self.account.id).count(), 1)
