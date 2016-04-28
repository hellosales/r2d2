import mock

from datetime import date
from freezegun import freeze_time

from r2d2.common_layer.models import CommonTransaction
from r2d2.squareup_api.models import ImportedSquareupPayment
from r2d2.squareup_api.models import SquareupAccount
from r2d2.squareup_api.tests.sample_data import PAYMENTS_RESPONSE
from r2d2.utils.test_utils import APIBaseTestCase


class TestImport(APIBaseTestCase):
    """ test if importer flow works """

    def setUp(self):
        self._create_user()
        self.account = SquareupAccount.objects.create(user=self.user, access_token='token', name='name')

    def tearDown(self):
        ImportedSquareupPayment.objects.filter(account_id=self.account.id).delete()
        CommonTransaction.objects.all().delete()

    def test_mapping(self):
        """ test correct mapping of object """
        self.fail()

    def test_import(self):
        """ test importing data from squareup """

        with freeze_time('2016-04-01'):
            with mock.patch('r2d2.squareup_api.models.SquareupAccount._call_payments_api') as mocked_call_payments:
                mocked_call_payments.return_value = PAYMENTS_RESPONSE

                self.account.fetch_status = SquareupAccount.FETCH_SCHEDULED
                self.account.fetch_data()

                self.assertEqual(ImportedSquareupPayment.objects.filter(account_id=self.account.id).count(), 3)
                isp = ImportedSquareupPayment.objects.filter(account_id=self.account.id).order_by('id')[0]
                self.assertEqual(isp.squareup_id, PAYMENTS_RESPONSE[0]['id'])
                self.assertNotEqual(isp.id.generation_time.date(), date(2014, 8, 25))

                self.assertEqual(CommonTransaction.objects.count(), 1)
                common_transaction = CommonTransaction.objects.all()[0]
                self.assertEqual(common_transaction.source, "SquareupAccount")
