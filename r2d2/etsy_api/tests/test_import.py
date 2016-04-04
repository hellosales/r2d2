import mock

from datetime import date
from freezegun import freeze_time

from r2d2.etsy_api.models import EtsyAccount
from r2d2.etsy_api.models import ImportedEtsyReceipt
from r2d2.etsy_api.models import ImportedEtsyShop
from r2d2.etsy_api.models import ImportedEtsyTransaction
from r2d2.etsy_api.tests import sample_data
from r2d2.utils.test_utils import APIBaseTestCase


class TestImport(APIBaseTestCase):
    """ test if importer flow works """

    def setUp(self):
        self._create_user()
        self.account = EtsyAccount.objects.create(user=self.user, access_token='token', name='name')

    def tearDown(self):
        ImportedEtsyReceipt.objects.filter(account_id=self.account.id).delete()
        ImportedEtsyShop.objects.filter(account_id=self.account.id).delete()
        ImportedEtsyTransaction.objects.filter(account_id=self.account.id).delete()

    def test_import(self):
        """ test importing data from shopify
            - call fetch_data for the first time - make sure we go with first import path, object is created & data
                of last transaction update is saved
            - call fetch_data for the second time - make sure we go with the update path, object should be updated
                (since the same one will be returned) """

        with mock.patch('etsy.Etsy.getUser') as mocked_user:
            mocked_user.return_value = sample_data.USER_RESPONSE
            with mock.patch('etsy.Etsy.findAllUserShops') as mocked_shops:
                mocked_shops.return_value = sample_data.SHOPS_RESPONSE
                with mock.patch('etsy.Etsy.findAllShopTransactions') as mocked_transactions:
                    mocked_transactions.return_value = sample_data.TRANSACTIONS_RESPONSE
                    with mock.patch('etsy.Etsy.findAllShopReceipts') as mocked_receipts:
                        mocked_receipts.return_value = sample_data.RECEIPTS_RESPONSE

                        self.account.fetch_status = EtsyAccount.FETCH_SCHEDULED
                        self.account.fetch_data()

                        mocked_user.assert_called_with(user_id='__SELF__')



        # with freeze_time('2016-04-01'):
        #         mocked_find.return_value = SHOPIFY_ORDERS['orders']

        #         mocked_find.assert_called_with(status='any', limit=ShopifyStore.MAX_REQUEST_LIMIT)

        #         self.assertEqual(ImportedShopifyOrder.objects.filter(account_id=self.account.id).count(), 1)
        #         iso = ImportedShopifyOrder.objects.filter(account_id=self.account.id)[0]
        #         self.assertEqual(iso.shopify_id, order_json['id'])
        #         self.assertNotEqual(iso.id.generation_time.date(), date(2014, 8, 25))

        #         self.account.fetch_status = ShopifyStore.FETCH_SCHEDULED
        #         self.account.fetch_data()
        #         mocked_find.assert_called_with(status='any', updated_at_min=iso.updated_at,
        #                                        limit=ShopifyStore.MAX_REQUEST_LIMIT)

        #         self.assertEqual(ImportedShopifyOrder.objects.filter(account_id=self.account.id).count(), 1)
