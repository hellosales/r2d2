import mock

from datetime import date
from decimal import Decimal
from freezegun import freeze_time
from shopify import Order

from django.utils import timezone

from r2d2.common_layer.models import CommonTransaction
from r2d2.shopify_api.models import ImportedShopifyOrder
from r2d2.shopify_api.models import ShopifyStore
from r2d2.shopify_api.tests.sample_data import SHOPIFY_ORDERS
from r2d2.utils.test_utils import APIBaseTestCase


SHOPIFY_MAPPED_DATA = {
    'transaction_id': 450789469,
<<<<<<< Updated upstream
    'currency_code':'USD',
=======
    'currency_code': 'USD',
>>>>>>> Stashed changes
    'date': u'2008-01-10T11:00:00-05:00',
    'products': [{
        'name': "IPod Nano - 8gb",
        'sku': "IPOD2008GREEN",
        'quantity': Decimal(1),
        'price': Decimal('199.00'),
        'tax': Decimal('3.98'),
        'discount': Decimal('0'),
        'total': Decimal('202.98')
    }, {
        'name': "IPod Nano - 8gb",
        'sku': "IPOD2008RED",
        'quantity': Decimal(1),
        'price': Decimal('199.00'),
        'tax': Decimal('3.98'),
        'discount': Decimal('0'),
        'total': Decimal('202.98')
    }, {
        'name': "IPod Nano - 8gb",
        'sku': "IPOD2008BLACK",
        'quantity': Decimal(1),
        'price': Decimal('199.00'),
        'tax': Decimal('3.98'),
        'discount': Decimal('0'),
        'total': Decimal('202.98')
    }
    ],
    'total_price': Decimal('398.00'),
    'total_tax': Decimal('11.94'),
    'total_discount': Decimal('0.00'),
    'total_total': Decimal('409.94')
}


class TestImport(APIBaseTestCase):
    """ test if importer flow works """

    def setUp(self):
        self._create_user()
        self.account = ShopifyStore.objects.create(user=self.user, access_token='token', name='name',
                                                   authorization_date=timezone.now())

    def tearDown(self):
        ImportedShopifyOrder.objects.filter(account_id=self.account.id).delete()
        CommonTransaction.objects.all().delete()

    def test_import(self):
        """ test importing data from shopify
            - call fetch_data for the first time - make sure we go with first import path, object is created & data
                of last transaction update is saved
            - call fetch_data for the second time - make sure we go with the update path, object should be updated
                (since the same one will be returned) """

        order_json = SHOPIFY_ORDERS['orders'][0]
        self.account._activate_session()

        with freeze_time('2016-04-01'):
            with mock.patch('shopify.Order.find') as mocked_find:
                mocked_find.return_value = [Order(attributes=x) for x in SHOPIFY_ORDERS['orders']]

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
                imported_shopify_order = ImportedShopifyOrder.objects.filter(account_id=self.account.id)[0]

                # test mapping
                mapped_data = self.account.map_data(imported_shopify_order)
                SHOPIFY_MAPPED_DATA['user_id'] = self.user.id
                self.assertEqual(mapped_data, SHOPIFY_MAPPED_DATA)

                # test if signal was called
                self.assertEqual(CommonTransaction.objects.count(), 1)
                common_transaction = CommonTransaction.objects.all()[0]
                self.assertEqual(common_transaction.source, "Shopify")
