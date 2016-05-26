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


class InsightsAPITestCase(APIBaseTestCase):
    """ tests for Insights API """
    def _add_transaction(self, user,):
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
            source='ShopifyStore',
        )

    def setUp(self):
        user = self._create_user()
        self.account = EtsyAccount.objects.create(user=self.user, name='name')
        self.account = ShopifyStore.objects.create(user=self.user, name='name')
        self.account = SquareupAccount.objects.create(user=self.user, name='name')

        for i in range(0, 30):
            Insight.objects.create(user=user, text="insight %d" % i, generator_class="FakeGenerator")

        for i in range(0, 5):
            self._add_transaction(user)

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
