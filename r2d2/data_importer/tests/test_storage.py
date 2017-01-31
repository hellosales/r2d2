from django.utils import timezone

from r2d2.common_layer.models import CommonTransaction
from r2d2.shopify_api.models import ImportedShopifyOrder
from r2d2.shopify_api.models import ShopifyStore
from r2d2.shopify_api.tests.sample_data import SHOPIFY_ORDERS
from r2d2.utils.test_utils import APIBaseTestCase


class TestStorage(APIBaseTestCase):
    """ test if storage model works correctly """

    def setUp(self):
        self._create_user()
        self.account = ShopifyStore.objects.create(user=self.user, access_token='token', name='name',
                                                   authorization_date=timezone.now())

    def tearDown(self):
        ImportedShopifyOrder.objects.filter(account_id=self.account.id).delete()
        CommonTransaction.objects.all().delete()

    def test_storage(self):
        """ test generic storage - based on shopify order
            - create object from json
            - make sure imported id is changed
            - make sure once created there is no possiblity to change account/user """

        order_json = SHOPIFY_ORDERS['orders'][0]
        ImportedShopifyOrder.create_from_json(self.account, order_json)

        self.assertEqual(ImportedShopifyOrder.objects.filter(account_id=self.account.id).count(), 1)
        iso = ImportedShopifyOrder.objects.filter(account_id=self.account.id)[0]
        self.assertNotEqual(iso.id, order_json['id'])
        self.assertEqual(iso.shopify_id, order_json['id'])

        iso.account_id = -1
        iso.user_id = -1
        iso.save()

        self.assertEqual(iso.account_id, self.account.id)
        self.assertEqual(iso.user_id, self.user.id)
        self.assertEqual(iso.prefix, 'shopify')
