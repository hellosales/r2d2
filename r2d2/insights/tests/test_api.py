# -*- coding: utf-8 -*-
""" tests for insights api """
from decimal import Decimal

from django.utils import timezone
from rest_framework.reverse import reverse

from r2d2.common_layer.models import CommonTransaction
from r2d2.etsy_api.models import EtsyAccount
from r2d2.insights.models import Insight
from r2d2.shopify_api.models import ShopifyStore
from r2d2.squareup_api.models import SquareupAccount
from r2d2.utils.test_utils import APIBaseTestCase
from r2d2.insights.serializers import HeaderDataSerializer
from freezegun import freeze_time


class InsightsAPITestCase(APIBaseTestCase):
    """ tests for Insights API """
    def _add_transaction(self, user, account):
        self._transaction_id = getattr(self, '_transaction_id', 0) + 1

        products = [{
            'name': 'name',
            'sku': 'sku',
            'quantity': Decimal(1.0),
            'price': Decimal(1.0),
            'tax': Decimal(0.0),
            'discount': Decimal(0.0),
            'total': Decimal(1.0)
        }]
        CommonTransaction.objects.create(
            user_id=user.id,
            transaction_id=str(self._transaction_id),
            date=timezone.now(),
            products=products,
            total_price=Decimal(1.0),
            total_tax=Decimal(0),
            total_discount=Decimal(0),
            total_total=Decimal(1.0),
            source='Shopify',
            currency_code='USD',
            data_provider_name=account.__class__.__name__,
            data_provider_id=account.id
        )

    def setUp(self):
        user = self._create_user()
        self.account = EtsyAccount.objects.create(user=self.user, name='name', access_token='fake token',
                                                  authorization_date=timezone.now())
        ct_account = ShopifyStore.objects.create(user=self.user, name='name', access_token='fake token',
                                                 authorization_date=timezone.now())
        self.account = ct_account
        self.account = SquareupAccount.objects.create(user=self.user, name='name', access_token='fake token',
                                                      authorization_date=timezone.now())

        for i in range(0, 30):
            with freeze_time('2015-%d-%d' % (i % 12 + 1, i / 2 + 1)):
                Insight.objects.create(user=user,
                                       text="insight %d" % i,
                                       generator_class="FakeGenerator",
                                       insight_model_id=1,
                                       is_initial=False,
                                       data_provider_name=ct_account.__class__.__name__,
                                       data_provider_id=ct_account.id)

        for i in range(0, 5):
            self._add_transaction(user, ct_account)

    def tearDown(self):
        CommonTransaction.objects.all().delete()

    def test_getting_insights(self):
        """ Insights shoulde be returned in two pages [page_size = 20 elements], there shoulde be
            paginator without counts used. Insights should be returned from the newest to the oldest """

        response = self.client.get(reverse('insights'))
        self.assertEqual(response.status_code, 401)

        self._login()
        response = self.client.get(reverse('insights'))
        self.assertEqual(response.status_code, 200)
        self.assertNotIn('count', response.data)
        self.assertIsNotNone(response.data['next'])
        self.assertEqual(len(response.data['results']), 20)
        self.assertEqual(response.data['results'][0]['text'], 'insight 29')
        self.assertEqual(response.data['results'][19]['text'], 'insight 10')
        self.assertEqual(response.data['results'][0]['created'], 'June 15')
        self.assertEqual(response.data['results'][19]['created'], 'Nov 6')

        response = self.client.get(response.data['next'])
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data['results']), 10)
        self.assertEqual(response.data['results'][0]['text'], 'insight 9')
        self.assertEqual(response.data['results'][9]['text'], 'insight 0')

    def test_getting_header(self):
        """ test getting instighs, transactions & channels number """
        response = self.client.get(reverse('header_data_api'))
        self.assertEqual(response.status_code, 401)

        self._login()
        response = self.client.get(reverse('header_data_api'))
        self.assertEqual(response.data['channels_number'], 3)
        self.assertEqual(response.data['insights_number'], 30)
        self.assertEqual(response.data['transactions_number'], 5)

    def test_number_formatting(self):
        """ test number formatting """
        self.assertEqual(HeaderDataSerializer._format_number(9999), 9999)
        self.assertEqual(HeaderDataSerializer._format_number(10000), "10.0K")
        self.assertEqual(HeaderDataSerializer._format_number(99999), "99.9K")
        self.assertEqual(HeaderDataSerializer._format_number(999999), "999K")
        self.assertEqual(HeaderDataSerializer._format_number(9999999), "9.9M")
