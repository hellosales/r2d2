import mock

from datetime import date
from decimal import Decimal
from freezegun import freeze_time

from django.utils import timezone

from r2d2.common_layer.models import CommonTransaction
from r2d2.squareup_api.models import ImportedSquareupPayment
from r2d2.squareup_api.models import SquareupAccount
from r2d2.squareup_api.tests.sample_data import PAYMENTS_RESPONSE
from r2d2.utils.test_utils import APIBaseTestCase


SQUAREUP_MAPPED_DATA = {
    'transaction_id': u'fZR0ZGHuHjprkXOtojv5S',
<<<<<<< Updated upstream
    'currency_code':u'USD',
=======
    'currency_code': u'USD',
>>>>>>> Stashed changes
    'date': u'2015-11-18T19:30:50Z',
    'products': [{
        'name': u'Custom Amount',
        'sku': u'',
        'quantity': Decimal("1"),
        'price': Decimal('1'),
        'tax': Decimal('0'),
        'discount': Decimal('0'),
        'total': Decimal('1')
    }],
    'total_price': Decimal('1'),
    'total_tax': Decimal('0'),
    'total_discount': Decimal('0'),
    'total_total': Decimal('1')
}


class TestImport(APIBaseTestCase):
    """ test if importer flow works """

    def setUp(self):
        self._create_user()
        self.account = SquareupAccount.objects.create(user=self.user, access_token='token', name='name',
                                                      authorization_date=timezone.now())

    def tearDown(self):
        ImportedSquareupPayment.objects.filter(account_id=self.account.id).delete()
        CommonTransaction.objects.all().delete()

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

                # test mapping
                mapped_data = self.account.map_data(isp)
                SQUAREUP_MAPPED_DATA['user_id'] = self.user.id
                self.assertEqual(mapped_data, SQUAREUP_MAPPED_DATA)

                self.assertEqual(CommonTransaction.objects.count(), 3)
                common_transaction = CommonTransaction.objects.all()[0]
                self.assertEqual(common_transaction.source, "Square")
