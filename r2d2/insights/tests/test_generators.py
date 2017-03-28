# -*- coding: utf-8 -*-
""" tests for insights generation """
from datetime import datetime, timedelta
from decimal import Decimal
from freezegun import freeze_time

from django.utils import timezone
import pandas as pd
import numpy as np

from r2d2.common_layer.models import CommonTransaction
from r2d2.insights.models import Insight, InsightHistorySummary
from r2d2.insights.generators import InsightDispatcher, InsightModel, DataImportedInsight,\
    AverageProductsPerTransactions, AverageTransactionsPerWeek
from r2d2.insights.signals import data_fetched
from r2d2.shopify_api.models import ShopifyStore
from r2d2.utils.test_utils import APIBaseTestCase
import r2d2.insights.generators as gen
import r2d2.common_layer.models as clmodels


class InsightsAPITestCase(APIBaseTestCase):
    """ tests for Insights generators """

    def _add_transaction(self, user, number_of_products, date, account):
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
            source='Shopify',
            currency_code='EUR',
            data_provider_name=account.__class__.__name__,
            data_provider_id=account.id
        )

    def create_insight_history(self, user, date, registered):
        plus_hour = timedelta(minutes=60)
        ct_account = ShopifyStore.objects.create(user=user,
                                                 name='name',
                                                 access_token='fake token',
                                                 authorization_date=timezone.now())

        for im in registered:
            Insight.objects.create(user=user,
                                   created=date,
                                   text=im.__class__.__name__ + ' test',
                                   generator_class=InsightDispatcher.__class__.__name__,
                                   insight_model_id=im.type_id,
                                   is_initial=False,
                                   data_provider_name=ct_account.__class__.__name__,
                                   data_provider_id=ct_account.id)
            date = date + plus_hour

    @freeze_time('2016-04-29')
    def setUp(self):
        user = self._create_user()
        self.account = ShopifyStore.objects.create(user=user, access_token='token', name='name',
                                                   authorization_date=timezone.now())
        week_ago = datetime.now() - timedelta(days=7)
        hour_ago = datetime.now() - timedelta(hours=1)

        # create some fake transactions:
        # - 3 for last week with avg 2 products per transaction (1, 2, 3)
        for i in range(1, 4):
            self._add_transaction(user, i, week_ago, self.account)
        # - 2 for today with avg 1.5 products per transaction (1, 2)
        for i in range(1, 3):
            self._add_transaction(user, i, hour_ago, self.account)

    def tearDown(self):
        CommonTransaction.objects.all().delete()
        Insight.objects.all().delete()

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

        # IMPORTANT! order of connect will be the order of insights
        data_fetched.connect(DataImportedInsight.handle_data_fetched)
        data_fetched.connect(AverageTransactionsPerWeek.handle_data_fetched)
        data_fetched.connect(AverageProductsPerTransactions.handle_data_fetched)

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

    def test_insight_dispatcher(self):
        """
        Test key InsightDispatcher methods:
        - initialize_insight_model_subcollections
        - insight_history_to_df
        - choose_insight_model
        - process_choices
        """
        user = self._create_user(i=2)
        hour_ago = datetime.now() - timedelta(hours=1)
        self.create_insight_history(user, hour_ago, (InsightDispatcher.get_registered_models()).values())

        # initialize_insight_model_subcollections
        registered_models = InsightDispatcher.get_registered_models()
        models_as_df = InsightDispatcher.initialize_insight_model_subcollections()
        self.assertEqual(models_as_df.shape[0], len(registered_models))
        self.assertTrue(np.array_equal(models_as_df.columns, ['type_id',
                                                              'class_name',
                                                              'periods',
                                                              'is_for_initial_pull',
                                                              'is_for_update_pull',
                                                              'is_limited',
                                                              'is_source_limited',
                                                              'is_product_limited',
                                                              'compares_sources',
                                                              'priority',
                                                              'shows_table']))
        for (type_id, model) in registered_models.iteritems():
            self.assertEqual(model.__class__.__name__,
                             models_as_df.loc[models_as_df.type_id == type_id, 'class_name'].values[0])
            self.assertEqual(model.periods,
                             models_as_df.loc[models_as_df.type_id == type_id, 'periods'].values[0])
            self.assertEqual(model.is_for_initial_pull,
                             models_as_df.loc[models_as_df.type_id == type_id, 'is_for_initial_pull'].values[0])
            self.assertEqual(model.is_for_update_pull,
                             models_as_df.loc[models_as_df.type_id == type_id, 'is_for_update_pull'].values[0])
            self.assertEqual(model.is_limited,
                             models_as_df.loc[models_as_df.type_id == type_id, 'is_limited'].values[0])
            self.assertEqual(model.is_source_limited,
                             models_as_df.loc[models_as_df.type_id == type_id, 'is_source_limited'].values[0])
            self.assertEqual(model.is_product_limited,
                             models_as_df.loc[models_as_df.type_id == type_id, 'is_product_limited'].values[0])
            self.assertEqual(model.compares_sources,
                             models_as_df.loc[models_as_df.type_id == type_id, 'compares_sources'].values[0])
            self.assertEqual(model.priority,
                             models_as_df.loc[models_as_df.type_id == type_id, 'priority'].values[0])
            self.assertEqual(model.shows_table,
                             models_as_df.loc[models_as_df.type_id == type_id, 'shows_table'].values[0])

        # insight_history_to_df
        ih = InsightHistorySummary.objects.all()
        ih_df = InsightDispatcher.insight_history_to_df(ih)
        self.assertEqual(models_as_df.shape[0], len(registered_models))
        self.assertTrue(np.array_equal(ih_df.columns, ['id',
                                                       'user_id',
                                                       'insight_model_id',
                                                       'count_insights',
                                                       'most_recent']))
        for insight in ih:
            self.assertEqual(insight.user_id, ih_df.loc[ih_df.id == insight.id, 'user_id'].values[0])
            self.assertEqual(insight.insight_model_id,
                             ih_df.loc[ih_df.id == insight.id, 'insight_model_id'].values[0])
            self.assertEqual(insight.count_insights,
                             ih_df.loc[ih_df.id == insight.id, 'count_insights'].values[0])

            # numpy to datetime conversion headaches below
            dt64ns = ih_df.loc[ih_df.id == insight.id, 'most_recent'].values[0]
            self.assertEqual(pd.to_datetime((insight.most_recent).replace(tzinfo=None)), pd.to_datetime(dt64ns))

        # process_choices
        # Note: this test only checks these things:
        #    1) If no InsightModels are passed it should return None
        #    2) At least one InsightModel is returned if the exclude_list is empty
        #    3) No insights are returned if the exclude_list contains all available InsightModels
        self.assertEqual(InsightDispatcher.process_choices(ih, None), None)
        self.assertTrue(isinstance(InsightDispatcher.process_choices(ih, models_as_df), InsightModel))
        self.assertEqual(InsightDispatcher.process_choices(ih, models_as_df, list(registered_models.values())), None)

    def test_data_frame_functions(self):
        """
        salesByChannel
        salesByPeriod
        topProducts
        normalizeDFColumns
        """
        txns = CommonTransaction.objects.all()
        txnsDF = clmodels.common_transactions_to_df(txns)
        txnsDF['value'] = Decimal(1.0)
        for column in clmodels.get_money_columns():
            txnsDF[column+'_converted'] = txnsDF[column] * txnsDF.value

        # salesByChannel
        out = gen.salesByChannel(txnsDF)
        test = txnsDF.groupby(['source'], as_index=False)
        test = test.agg({'product_quantity': 'sum', 'product_total_converted': 'sum'})
        self.assertEqual(gen.salesByChannel(None), None)
        self.assertTrue(test.product_quantity.equals(out.product_quantity))
        self.assertTrue(test.product_total_converted.equals(out.product_total_converted))

        # salesByPeriod
        self.assertEqual(gen.salesByPeriod(None, 'year'), None)
        periods = {'year': '1A',
                   'quarter': '1Q',
                   'month': '1M',
                   '7 days': '7D',
                   '30 days': '30D',
                   '365 days': '365D',
                   'week': '1W',
                   'day': '1D',
                   'hour': '1H'}

        for (period, freq) in periods.iteritems():
            test = txnsDF
            grouper = pd.TimeGrouper(freq)
            test.index = test.date
            test = test.groupby(grouper)
            test = test.agg({'product_quantity': 'sum', 'product_total_converted': 'sum'})
            out = gen.salesByPeriod(txnsDF, period, False)

            self.assertTrue(out.product_quantity.equals(test.product_quantity))
            self.assertTrue(out.product_total_converted.equals(test.product_total_converted))

            test = txnsDF
            test.index = test.date
            test = test.groupby([grouper, 'product_name', 'product_sku'])
            test = test.agg({'product_quantity': 'sum', 'product_total_converted': 'sum'})
            out = gen.salesByPeriod(txnsDF, period, True)
            self.assertTrue(out.product_quantity.equals(test.product_quantity))
            self.assertTrue(out.product_total_converted.equals(test.product_total_converted))

        # topProducts
        test = txnsDF
        test = test.groupby(['product_name'], as_index=False)
        test = test.agg({'product_quantity': 'sum', 'product_total_converted': 'sum'})
        test = test.sort_values(by=['product_total_converted', 'product_quantity'], ascending=False)
        out = gen.topProducts(txnsDF)
        self.assertEqual(gen.topProducts(None), None)
        self.assertTrue(test.product_total_converted.equals(out.product_total_converted))
        self.assertTrue(test.product_quantity.equals(out.product_quantity))

        # normalizeDFColumns
        test = txnsDF
        columnDict = {'date': 'Date',
                      'total_price': 'Total Price',
                      'total_tax': 'Tax',
                      'total_discount': 'Discount',
                      'total_total': 'Total',
                      'currency_code': 'Currency',
                      'source': 'Channel',
                      'product_name': 'Name',
                      'product_sku': 'SKU',
                      'product_quantity': 'Item Quantity',
                      'product_price': 'Price',
                      'product_tax': 'Item Tax',
                      'product_discount': 'Item Discount',
                      'product_total': 'Item Total',
                      'share': "Share",
                      'total_price_converted': 'Total Price',
                      'total_tax_converted': 'Tax',
                      'total_discount_converted': 'Discount',
                      'total_total_converted': 'Total',
                      'product_price_converted': 'Price',
                      'product_tax_converted': 'Item Tax',
                      'product_discount_converted': 'Item Discount',
                      'product_total_converted': 'Item Total',
                      'value': 'Exchange Rate'}
        self.assertTrue(test.rename(columns=columnDict).equals(gen.normalizeDFColumns(txnsDF)))

    def test_time_functions(self):
        """
        Test generators.py support functions having to do with time:

        isBeginningOfPeriod
        getPreviousYear
        getPreviousMonth
        getPreviousWeek
        getPreviousPeriod
        """
        a_date = datetime(2016, 1, 1)
        special_dates = [a_date]

        # year checking
        (period, start_date, end_date) = gen.isBeginningOfPeriod(a_date) or (None, None, None)
        self.assertEqual(period, "year")
        self.assertEqual(start_date, a_date.replace(year=a_date.year-1))
        self.assertEqual(end_date, a_date - timedelta(microseconds=1))

        # month checks
        one_date = a_date.replace(month=2)
        one_microsecond = timedelta(microseconds=1)
        while True:
            special_dates.append(one_date)
            (period, start_date, end_date) = gen.isBeginningOfPeriod(one_date) or (None, None, None)
            self.assertEqual(period, "month")
            self.assertEqual(start_date, one_date.replace(month=one_date.month-1))
            self.assertEqual(end_date, one_date - one_microsecond)

            if one_date.month == 12:
                break
            else:
                one_date = a_date.replace(month=one_date.month+1)

        # week checks
        one_date = a_date.replace(day=4)  # First Monday of the year
        plus_7 = timedelta(days=7)
        while one_date.year < 2017:
            special_dates.append(one_date)
            (period, start_date, end_date) = gen.isBeginningOfPeriod(one_date) or (None, None, None)

            if one_date.day == 1:  # A month beginning
                self.assertEqual(period, "month")
            else:
                self.assertEqual(period, "week")
                this_monday = one_date - timedelta(days=one_date.weekday())
                self.assertEqual(start_date, this_monday - plus_7)
                self.assertEqual(end_date, this_monday - one_microsecond)

            one_date = one_date + plus_7

        # check no other dates are special
        one_day = timedelta(days=1)
        one_date = a_date + one_day
        counter = 1
        while counter < 366:
            if one_date in special_dates:
                counter += 1
                continue

            (period, start_date, end_date) = gen.isBeginningOfPeriod(one_date) or (None, None, None)
            self.assertEqual(period, None)

            (start_date, end_date) = gen.getPreviousYear(one_date)
            self.assertEqual(a_date.replace(year=a_date.year-1), start_date)
            self.assertEqual(a_date - one_microsecond, end_date)

            (start_date, end_date) = gen.getPreviousMonth(one_date)
            if one_date.month == 1:
                self.assertEqual(one_date.replace(month=one_date.month + 11, year=one_date.year-1, day=1), start_date)
            else:
                self.assertEqual(one_date.replace(month=one_date.month - 1, day=1), start_date)
            self.assertEqual(one_date.replace(day=1) - one_microsecond, end_date)

            (start_date, end_date) = gen.getPreviousWeek(one_date)
            delta_to_monday = timedelta(days=one_date.weekday())
            self.assertEqual(one_date - delta_to_monday - plus_7, start_date)
            self.assertEqual(one_date - delta_to_monday - one_microsecond, end_date)

            one_date = one_date + one_day
            counter += 1

    def test_formatters(self):
        """
        periodFormatter
        integerTableFormat
        dollarTableFormat
        percentTableFormat
        fancyDateTimeDeltaFormat
        """
        now = datetime(2016, 4, 29)
        self.assertEqual(gen.periodFormatter(now, 'year'), '2016')
        self.assertEqual(gen.periodFormatter(now, 'quarter'), '04/29/16')
        self.assertEqual(gen.periodFormatter(now, 'month'), 'April')
        self.assertEqual(gen.periodFormatter(now, 'week'), '04/29/16')
        self.assertEqual(gen.periodFormatter(now, 'day'), '04/29/16')
        self.assertEqual(gen.periodFormatter(now, 'hour'), 'Fri Apr 29 00:00:00 2016')
        self.assertEqual(gen.periodFormatter(now, 'foo'), None)

        self.assertEqual(gen.integerTableFormat(1.00), '1')
        self.assertEqual(gen.dollarTableFormat(1.00), '$1.00')
        self.assertEqual(gen.percentTableFormat(1.00), '100.00%')
        self.assertEqual(gen.fancyDateTimeDeltaFormat(now, now.replace(year=now.year + 1, month=now.month+3), 1),
                         '1 year')
        self.assertEqual(gen.fancyDateTimeDeltaFormat(now, now.replace(year=now.year + 1, month=now.month+3), 2),
                         '1 year, 3 months')
        self.assertEqual(gen.fancyDateTimeDeltaFormat(now.replace(month=now.month - 3, day=now.day-14), now, 3),
                         '3 months, 15 days')
