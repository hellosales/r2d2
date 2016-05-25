# -*- coding: utf-8 -*-
""" tests for insights generation """
from datetime import datetime
from datetime import timedelta
from decimal import Decimal
from freezegun import freeze_time

from r2d2.common_layer.models import CommonTransaction
from r2d2.insights.models import Insight
from r2d2.insights.signals import data_fetched
from r2d2.shopify_api.models import ShopifyStore
from r2d2.utils.test_utils import APIBaseTestCase


class InsightsAPITestCase(APIBaseTestCase):
    """ tests for Insights generators """

    def _add_transaction(self, user, number_of_products, date):
        self._transaction_id = getattr(self, '_transaction_id', 0) + 1

        products = []
        for dummy in range(0, number_of_products):
            products.append({
                'name': 'name',
                'sku': 'sku',
                'quantity': Decimal(1.0),
                'price': Decimal(1.0),
                'tax': Decimal(0.0),
                'discount': Decimal(0.0),
                'total': Decimal(1.0)
            })
        CommonTransaction.objects.create(
            user_id=user.id,
            transaction_id=str(self._transaction_id),
            date=date,
            products=products,
            total_price=Decimal(number_of_products * 1.0),
            total_tax=Decimal(0),
            total_discount=Decimal(0),
            total_total=Decimal(number_of_products * 1.0),
            source='ShopifyStore',
        )

    @freeze_time('2016-04-29')
    def setUp(self):
        user = self._create_user()
        self.account = ShopifyStore.objects.create(user=user, access_token='token', name='name')
        week_ago = datetime.now() - timedelta(days=7)
        hour_ago = datetime.now() - timedelta(hours=1)

        # create some fake transactions:
        # - 3 for last week with avg 2 products per transaction (1, 2, 3)
        for i in range(1, 4):
            self._add_transaction(user, i, week_ago)
        # - 2 for today with avg 1.5 products per transaction (1, 2)
        for i in range(1, 3):
            self._add_transaction(user, i, hour_ago)

    def tearDown(self):
        CommonTransaction.objects.all().delete()

    def test_generating_insights(self):
        """ - there should be no insights at the beginning
            - send data_fetched signal with fetched_from_all = False - there should be still no insights
            - send data_fetched signal with fetched_from_all = True - there should be three signals:
                - "Transactions data was imported"
                - "Number of transactions in last 24h increased from 0.43 to 2 compared to previous week"
                - "Average number of products per transaction in last 24h decreased from 2 to 1.5 compared to
                   previous week"
            - move time one month ahead & send data_fetched signal with fetched_from_all
                - "Transactions data was updated" is created """

        with freeze_time('2016-04-29'):
            # there should be no insights at the beginning
            self.assertEqual(Insight.objects.count(), 0)

            # send data_fetched signal with fetched_from_all = False
            data_fetched.send(sender=None, account=self.account, success=True, fetched_from_all=False)
            self.assertEqual(Insight.objects.count(), 0)

            # send data_fetched signal with fetched_from_all = True
            data_fetched.send(sender=None, account=self.account, success=True, fetched_from_all=True)
            self.assertEqual(Insight.objects.count(), 3)
            insights = Insight.objects.all().order_by('created')
            self.assertEqual(insights[0].text, "Transactions data was imported")
            self.assertEqual(insights[1].text, ("Number of transactions in last 24h increased from 0.43 to 2 compared "
                                                "to previous week"))
            self.assertEqual(insights[2].text, ("Average number of products per transaction in last 24h decreased from "
                                                "2.00 to 1.50 compared to previous week"))

        with freeze_time('2016-05-29'):
            data_fetched.send(sender=None, account=self.account, success=True, fetched_from_all=True)
            self.assertEqual(Insight.objects.count(), 4)
            insight = Insight.objects.all().order_by('-created')[0]
            self.assertEqual(insight.text, "Transactions data was updated")
