import mock

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
        self.account = EtsyAccount.objects.create(user=self.user, access_token='oauth_token=x&oauth_token_secret=y',
                                                  name='name')

    def tearDown(self):
        ImportedEtsyReceipt.objects.filter(account_id=self.account.id).delete()
        ImportedEtsyShop.objects.filter(account_id=self.account.id).delete()
        ImportedEtsyTransaction.objects.filter(account_id=self.account.id).delete()

    def test_import(self):
        """ test importing data from etsy """

        with mock.patch('r2d2.etsy_api.models.EtsyAccount._prepare_api') as mocked_api:
            mocked_api.return_value = True
            with mock.patch('r2d2.etsy_api.models.EtsyAccount._call_fetch_user') as mocked_user:
                mocked_user.return_value = sample_data.USER_RESPONSE
                with mock.patch('r2d2.etsy_api.models.EtsyAccount._call_fetch_shops') as mocked_shops:
                    mocked_shops.return_value = sample_data.SHOPS_RESPONSE
                    with mock.patch('r2d2.etsy_api.models.EtsyAccount._call_fetch_transactions') as mocked_transactions:
                        mocked_transactions.return_value = sample_data.TRANSACTIONS_RESPONSE
                        with mock.patch('r2d2.etsy_api.models.EtsyAccount._call_fetch_receipts') as mocked_receipts:
                            mocked_receipts.return_value = sample_data.RECEIPTS_RESPONSE

                            self.account.fetch_status = EtsyAccount.FETCH_SCHEDULED
                            self.account.fetch_data()

                            mocked_user.assert_called_with(user_id='__SELF__')
                            mocked_shops.assert_called_with(limit=100, user_id=28651835)
                            mocked_transactions.assert_called_with(limit=100, shop_id=12153339, offset=0)
                            mocked_receipts.assert_called_with(limit=100, shop_id=12153339, offset=0)

                            kwargs = {'account_id': self.account.id}
                            self.assertEqual(ImportedEtsyShop.objects.filter(**kwargs).count(), 1)
                            self.assertEqual(ImportedEtsyTransaction.objects.filter(**kwargs).count(), 2)
                            self.assertEqual(ImportedEtsyReceipt.objects.filter(**kwargs).count(), 1)
