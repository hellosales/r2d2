import mock

from datetime import datetime
from decimal import Decimal
from freezegun import freeze_time

from django.utils import timezone

from r2d2.common_layer.models import CommonTransaction
from r2d2.stripe_api.models import ImportedStripeOrder
from r2d2.stripe_api.models import StripeAccount
from r2d2.stripe_api.tests.sample_data import STRIPE_TEST_ORDER_RESPONSE
from r2d2.utils.test_utils import APIBaseTestCase


STRIPE_MAPPED_DATA = {
    'currency_code': u'USD',
    'date': datetime(2017, 2, 27, 15, 27, 54),
    'products': [{
                  'discount': Decimal('0'),
                  'name': u'Flannel Scarf',
                  'price': Decimal('0.7'),
                  'quantity': Decimal('1'),
                  'sku': u'000003',
                  'tax': Decimal('0'),
                  'total': Decimal('0.7')}],
    'total_discount': Decimal('0'),
    'total_price': Decimal('0.7'),
    'total_tax': Decimal('0'),
    'total_total': Decimal('0.7'),
    'transaction_id': u'or_19rv66Bm6CxpShfN1YI56AHH',
    'user_id': 1L}


class TestImport(APIBaseTestCase):
    """ test if importer flow works """

    def setUp(self):
        self._create_user()
        self.account = StripeAccount.objects.create(user=self.user,
                                                    access_token='token',
                                                    name='name',
                                                    authorization_date=timezone.now())

    def tearDown(self):
        ImportedStripeOrder.objects.filter(account_id=self.account.id).delete()
        CommonTransaction.objects.all().delete()

    def test_import(self):
        """ test importing data from stripe """

        with mock.patch('r2d2.stripe_api.models.StripeAccount._call_fetch_orders') as mocked_orders:
            mocked_orders.return_value.auto_paging_iter.return_value = iter(STRIPE_TEST_ORDER_RESPONSE['data'])

            self.account.fetch_status = StripeAccount.FETCH_SCHEDULED
            self.account.fetch_data()

            kwargs = {'account_id': self.account.id}
            self.assertEqual(ImportedStripeOrder.objects.filter(**kwargs).count(), 3)

            # test mapping
            imported_order = ImportedStripeOrder.objects.filter(**kwargs).order_by('id')
            mapped_data = self.account.map_data(imported_order[0])
            STRIPE_MAPPED_DATA['user_id'] = self.user.id
            self.assertEqual(mapped_data, STRIPE_MAPPED_DATA)

            self.assertEqual(CommonTransaction.objects.count(), 3)
            common_transaction = CommonTransaction.objects.all()[0]
            self.assertEqual(common_transaction.source, "Stripe")
