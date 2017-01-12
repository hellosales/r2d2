# -*- coding: utf-8 -*-
""" tests for basic functionality of common layer - creating & updating objects on signals """
from datetime import date
from datetime import datetime
from datetime import timedelta
from freezegun import freeze_time
from decimal import Decimal

from django.utils import timezone
import pandas as pd

from r2d2.common_layer.models import CommonTransaction, ExchangeRate, ExchangeRateSource
from r2d2.common_layer.currency import MoneyConverter
import r2d2.common_layer.models as clmodels
import r2d2.common_layer.currency as curr
from r2d2.common_layer.signals import object_imported
from r2d2.etsy_api.models import EtsyAccount
from r2d2.shopify_api.models import ShopifyStore
from r2d2.utils.test_utils import APIBaseTestCase


class TestBase(APIBaseTestCase):
    """ test basic common layer functionality """

    def _get_sample_transaction(self, transaction_id, date):
        return {
            'user_id': 1,
            'transaction_id': transaction_id,
            'date': date,
            'products': [{
                'name': "test",
                'sku': "whateva",
                'quantity': 1,
                'price': 10.0,
                'tax': 1.0,
                'discount': 2.0,
                'total': 9.0
            }],
            'total_price': 10.0,
            'total_tax': 1.0,
            'total_discount': 2.0,
            'total_total': 9.0,
            'currency_code': 'EUR',
        }

    def setUp(self):
        self._create_user()
        self.shopify_account = ShopifyStore.objects.create(user=self.user, access_token='token', name='name',
                                                           authorization_date=timezone.now())
        self.etsy_account = EtsyAccount.objects.create(user=self.user,
                                                       access_token='oauth_token=x&oauth_token_secret=y', name='name',
                                                       authorization_date=timezone.now())
        source = ExchangeRateSource.objects.create(id=1,
                                                   name='USD',
                                                   last_update=timezone.now().date(),
                                                   base_currency='USD')
        ExchangeRate.objects.create(id=1,
                                    currency='EUR',
                                    value=Decimal(10),
                                    source=source,
                                    date=timezone.now().date()-timedelta(days=1))
        ExchangeRate.objects.create(id=2,
                                    currency='EUR',
                                    value=Decimal(100),
                                    source=source,
                                    date=timezone.now().date())

    def tearDown(self):
        CommonTransaction.objects.all().delete()
        ExchangeRate.objects.all().delete()
        ExchangeRateSource.objects.all().delete()

    @freeze_time('2016-08-28')
    def test_all(self):
        """ - Test creating object on signal
            - Test updating object on signal
            - Test if there is no collision for objects with same ID but different sources
            - Test CommonTransaction to pandas.DataFrame conversion
            - Test currency conversion of CommonTransaction DataFrame
        """

        now = datetime.now()

        # test creating object on signal
        self.assertEqual(CommonTransaction.objects.count(), 0)
        sample_object = self._get_sample_transaction(1, now)
        object_imported.send(sender=None, importer_account=self.shopify_account, mapped_data=sample_object)
        self.assertEqual(CommonTransaction.objects.count(), 1)

        # test updating object on signal
        sample_object = self._get_sample_transaction(1, now + timedelta(days=1))
        object_imported.send(sender=None, importer_account=self.shopify_account, mapped_data=sample_object)
        self.assertEqual(CommonTransaction.objects.count(), 1)
        common_transaction = CommonTransaction.objects.all()[0]
        self.assertEqual(common_transaction.date, now + timedelta(days=1))
        self.assertEqual(common_transaction.source, "Shopify")

        # test if there is no collision for objects with same ID but different sources
        sample_object = self._get_sample_transaction(1, now)
        object_imported.send(sender=None, importer_account=self.etsy_account, mapped_data=sample_object)
        self.assertEqual(CommonTransaction.objects.count(), 2)

        # sanity check
        sample_object = self._get_sample_transaction(2, now)
        object_imported.send(sender=None, importer_account=self.shopify_account, mapped_data=sample_object)
        self.assertEqual(CommonTransaction.objects.count(), 3)

        # test CommonTransaction to pandas.DataFrame conversion.  Test that we
        # get the same number of rows as in the DB, and that a lookup returns the
        # same data
        test_df = clmodels.common_transactions_to_df([common_transaction])
        self.assertEqual(1, len(test_df.index))
        self.assertEqual(test_df.user_id.iloc[0], common_transaction.user_id)
        self.assertEqual(test_df.transaction_id.iloc[0], common_transaction.transaction_id)
        self.assertEqual(test_df.date.iloc[0], common_transaction.date)
        self.assertEqual(test_df.total_price.iloc[0], common_transaction.total_price)
        self.assertEqual(test_df.total_tax.iloc[0], common_transaction.total_tax)
        self.assertEqual(test_df.total_discount.iloc[0], common_transaction.total_discount)
        self.assertEqual(test_df.total_total.iloc[0], common_transaction.total_total)
        self.assertEqual(test_df.currency_code.iloc[0], common_transaction.currency_code)
        self.assertEqual(test_df.source.iloc[0], common_transaction.source)
        self.assertEqual(test_df.product_name.iloc[0], common_transaction.products[0].name)
        self.assertEqual(test_df.sku.iloc[0], common_transaction.products[0].sku)
        self.assertEqual(test_df.product_quantity.iloc[0], common_transaction.products[0].quantity)
        self.assertEqual(test_df.product_price.iloc[0], common_transaction.products[0].price)
        self.assertEqual(test_df.product_tax.iloc[0], common_transaction.products[0].tax)
        self.assertEqual(test_df.product_discount.iloc[0], common_transaction.products[0].discount)
        self.assertEqual(test_df.product_total.iloc[0], common_transaction.products[0].total)

        # test currency conversion
        rates = ExchangeRate.objects.all()
        test_df.date = pd.to_datetime(rates[0].date)  # reset date to that of one of our rates to force a match
        test_df_converted = curr.convert_common_transactions_df(test_df.copy(), 'USD', True)
        this_rate = ExchangeRate.objects.filter(currency=common_transaction.currency_code, date=test_df.date.iloc[0])[0]
        self.assertEqual(test_df_converted.value.iloc[0], this_rate.value)
        self.assertEqual(test_df_converted.total_total_converted.iloc[0],
                         this_rate.value*common_transaction.total_total)
        self.assertEqual(test_df_converted.total_discount_converted.iloc[0],
                         this_rate.value*common_transaction.total_discount)
        self.assertEqual(test_df_converted.total_price_converted.iloc[0],
                         this_rate.value*common_transaction.total_price)
        self.assertEqual(test_df_converted.total_tax_converted.iloc[0],
                         this_rate.value*common_transaction.total_tax)
        self.assertEqual(test_df_converted.product_price_converted.iloc[0],
                         this_rate.value*common_transaction.products[0].price)
        self.assertEqual(test_df_converted.product_tax_converted.iloc[0],
                         this_rate.value*common_transaction.products[0].tax)
        self.assertEqual(test_df_converted.product_discount_converted.iloc[0],
                         this_rate.value*common_transaction.products[0].discount)
        self.assertEqual(test_df_converted.product_total_converted.iloc[0],
                         this_rate.value*common_transaction.products[0].total)
