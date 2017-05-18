# -*- coding: utf-8 -*-
""" insights generators
    each generator must be connected with fetched_data signal in order to work """
import logging
from bson.code import Code
from datetime import datetime, timedelta
from functools import partial
from collections import OrderedDict
from decimal import Decimal
import importlib
import math

import pandas as pd
import numpy as np

from django.db import transaction

from r2d2.common_layer.models import CommonTransaction
from r2d2.common_layer.models import CommonTransactionDataFrame as CTDF
import r2d2.common_layer.models as clmodels
import r2d2.common_layer.currency as curr

logger = logging.getLogger('django')


class BaseGenerator(object):
    """ Base generator class """
    EMAIL_NOTIFICATION = True

    @classmethod
    def should_be_triggered(cls, account, success, fetched_from_all):
        raise NotImplementedError

    @classmethod
    def trigger(cls, account, success, fetched_from_all):
        raise NotImplementedError

    @classmethod
    def handle_data_fetched(cls, **kwargs):
        account = kwargs['account']  # the user account
        success = kwargs['success']  # the status of the fetch
        fetched_from_all = kwargs['fetched_from_all']

        if cls.should_be_triggered(account, success, fetched_from_all):
            (insight, channels, products) = cls.trigger(account, success, fetched_from_all) or (None, None, None)
            if insight:
                # explicit transaction here to allow channels and products to be saved before post_save is called
                with transaction.atomic():
                    insight.user = account.user
                    insight.data_provider_name = account.__class__.__name__
                    insight.data_provider_id = account.id
                    insight.generator_class = cls.__name__
                    insight.save()

                    if channels:
                        # change this to insight.product_set.set(channels) if upgrading to Django 1.10+
                        insight.channel_set = channels

                    if products:
                        # change this to insight.product_set.set(products) if upgrading to Django 1.10+
                        insight.product_set = products


class InsightModel(object):
    """
    Metadata and logic class for a potential insight for the InsightDispatcher to choose.
    Contains generic data about how it can be used, as well as specific data about
    how it was used with a particular Insight
    priority: 1-10, 1 being most important, 10 least important
    """
    type_id = None  # the unique ID of the InsightModel
    periods = []  # periods insight should be used for period analysis:  'year', 'month', 'week', or empty list
    is_for_initial_pull = False  # whether Insight should be used for the initial transaction pull
    is_for_update_pull = False  # whether Insight should be used for transaction updates
    is_limited = False  # whether Insight should not be used repeatedly
    is_source_limited = False  # whether Insight should not be used repeatedly for the same source
    is_product_limited = False  # whether Insight should not be used repeatedly for the same product
    compares_sources = False  # whether the Insight compares data across sources
    priority = None  # the relative importance of this Insight
    shows_table = False  # whether this insight shows a table
    output_message = None  # the template message this insight will provide

    def execute(self, user_id, source, txns, period=None, **kwargs):
        """
        The method that will generate this insight.  This will return a complete
        message that can be displayed to the merchant
        """
        raise NotImplementedError


class InsightDispatcher(BaseGenerator):
    """
    Dispatcher decides which insight to show once a signal is sent:
    1.  If this is an initial insight, choose that
    2.  If this is a pull that allows for a period (year, month, week) closing insight, choose that.
        Note:  If there are no txns for the period go to 3
    3.  Otherwise push an insight for the last pull.  If there are no txns, no insight
    """
    EMAIL_NOTIFICATION = True
    __module = importlib.import_module("r2d2.insights.generators")

    # Collections of models
    __registered_insight_models = {}
    __insight_models_df = None
    __initial_insight_models = None  # Models that output initial insights
    __periodic_insight_models = None  # Models that output periodic insights
    __update_insight_models = None  # Models that output all other update insights

    @classmethod
    def register(cls, registered_insight_model, iid):
        """
        adds insight_model to the registered pool
        only registered insights_model will be available to serve
        """
        assert hasattr(registered_insight_model, 'execute') and callable(registered_insight_model.execute)

        instance = registered_insight_model()
        instance.type_id = iid
        cls.__registered_insight_models[iid] = instance

    @classmethod
    def list_registered(cls):
        return cls.__registered_insight_models.values()

    @classmethod
    def get_registered_models(cls):
        return cls.__registered_insight_models

    @classmethod
    def get_model_by_name(cls, name):
        for model in cls.__registered_insight_models.itervalues():
            if model.__name__ == name:
                return model
        return None

    @classmethod
    def should_be_triggered(cls, account, success, fetched_from_all):
        return success

    @classmethod
    def initialize_insight_model_subcollections(cls):
        if len(cls.__registered_insight_models) == 0:
            return

        type_id = []
        class_name = []
        periods = []
        is_for_initial_pull = []
        is_for_update_pull = []
        is_limited = []
        is_source_limited = []
        is_product_limited = []
        compares_sources = []
        priority = []
        shows_table = []

        columns = ['type_id',
                   'class_name',
                   'periods',
                   'is_for_initial_pull',
                   'is_for_update_pull',
                   'is_limited',
                   'is_source_limited',
                   'is_product_limited',
                   'compares_sources',
                   'priority',
                   'shows_table']

        for im in cls.__registered_insight_models.values():
            type_id.append(im.type_id)
            class_name.append(im.__class__.__name__)
            periods.append(im.periods)
            is_for_initial_pull.append(im.is_for_initial_pull)
            is_for_update_pull.append(im.is_for_update_pull)
            is_limited.append(im.is_limited)
            is_source_limited.append(im.is_source_limited)
            is_product_limited.append(im.is_product_limited)
            compares_sources.append(im.compares_sources)
            priority.append(im.priority)
            shows_table.append(im.shows_table)

        zipped = zip(type_id,
                     class_name,
                     periods,
                     is_for_initial_pull,
                     is_for_update_pull,
                     is_limited,
                     is_source_limited,
                     is_product_limited,
                     compares_sources,
                     priority,
                     shows_table)

        cls.__insight_models_df = pd.DataFrame(zipped, columns=columns)
        cls.__initial_insight_models = cls.__insight_models_df[cls.__insight_models_df.is_for_initial_pull]
        cls.__periodic_insight_models = cls.__insight_models_df[~cls.__insight_models_df.periods.isnull()]
        cls.__update_insight_models = cls.__insight_models_df[cls.__insight_models_df.is_for_update_pull &
                                                              cls.__insight_models_df.periods.isnull()]

        return cls.__insight_models_df

    @classmethod
    def insight_history_to_df(cls, insight_history=None):
        """
        Turns QuerySet of InsightHistorySummary from the DB into a DataFrame
        Returns None if passed insight history is empty
        """
        if len(insight_history) == 0:
            return None

        iid = []
        user_id = []
        insight_model_id = []
        count_insights = []
        most_recent = []

        columns = ['id',
                   'user_id',
                   'insight_model_id',
                   'count_insights',
                   'most_recent']

        for i in insight_history:
            iid.append(i.id),
            user_id.append(i.user_id)
            insight_model_id.append(i.insight_model_id)
            count_insights.append(i.count_insights)
            most_recent.append(i.most_recent)

        zipped = zip(iid,
                     user_id,
                     insight_model_id,
                     count_insights,
                     most_recent)

        return pd.DataFrame(zipped, columns=columns)

    @classmethod
    def choose_insight_model(cls, user_id, source, fetched_from_all, period=None,
                             insight_history=None, exclude_list=None, is_initial=False):
        """
        Determines which InsightModel to use to generate the next Insight.
        The is the heart of the InsightModel choosing process.
        TODO: look at more criteria to choose InsightModel (channels, products, whether it was helpful, etc)
        """
        # Generate the collection if not yet initialized
        if cls.__insight_models_df is None:
            cls.initialize_insight_model_subcollections()

        # First subset our insights
        if is_initial:  # First fetch insights
            choices = cls.__initial_insight_models
        elif period is not None:  # period insights
            choices = cls.__periodic_insight_models
            choices = choices[choices.periods.apply(lambda x: period in x)]  # IMs than include period in periods lists
        else:  # Update insights not tied to periods
            choices = cls.__update_insight_models

        im = cls.process_choices(insight_history, choices, exclude_list)

        return im

    @classmethod
    def process_choices(cls, ih, ims, exclude_list=None):
        """
        Processes the passed Insight history, possible InsightModels, and list of
        InsightModels to exclude to return the non-excluded insight that's been served
        least recently, with the highest priority, with the smallest served count.
        Note that priority 0 insights are always served up unless excluded.

        ih: iterable of InsightHistorySummary objects
        ims: dataframe of InsightModels
        exclude_list: iterable of InsightModels objects

        This is a separate method so that multiple decision algorithms can be implemented
        and used interchangeably in the future.
        """
        if ims is None or ims.shape[0] == 0:
            return None

        # Grab IDs from exclude_list if not null
        excluded_ids = []
        if exclude_list is not None:
            for excluded in exclude_list:
                excluded_ids.append(excluded.type_id)

        # get all insight_models and count of how many times they've been used,
        # along with last used date.  Then pick the one that's been served
        # least recently, with the highest priority, with the smallest served count
        # SQL pseudo-code:
        # SELECT IH.user_id,
        #    IM.type_id,
        #    count(IH.*),
        #    max(IH.created),
        #    IM.priority
        # FROM IM
        # LEFT JOIN IH
        # ON IM.type_id = IH.insight_model_id
        # GROUP BY IM.type_id, IH.user_id

        ih_df = cls.insight_history_to_df(ih)

        # Exclude if needed
        choices = ims.loc[~ims.type_id.isin(excluded_ids)]

        # left outer join equivalent if possible, otherwise create empty columns
        if ih_df is not None:
            choices = pd.merge(choices, ih_df, left_on="type_id", right_on="insight_model_id", how="left")
        elif choices.shape[0] == 0:
            return None
        else:
            choices.loc[:, 'count_insights'] = None
            choices.loc[:, 'most_recent'] = None

        # return a 0-priority IM if available
        zero_priority = choices[choices.priority == 0]
        if zero_priority.shape[0] != 0:
            choices = zero_priority

        # fill NaN and NaT then sort
        choices.count_insights = choices.count_insights.fillna(0)
        choices.most_recent = choices.most_recent.fillna(0)
        choices = choices.sort_values(by=['most_recent', 'priority', 'count_insights'],
                                      ascending=[True, False, True])
        if choices.shape[0] == 0:
            return None

        # pick first off the list
        im = cls.__registered_insight_models[choices.type_id.iloc[0]]
        return im

    @classmethod
    def trigger(cls, account, success, fetched_from_all):
        """
        The meat of the InsightDispatcher.  Checks for initial pull, whether it's
        the beginning of a new period, and generates an insight based on those
        criteria.
        """
        from r2d2.insights.models import Insight, InsightHistorySummary
        im_params = {}
        rolling_window = True
        period = None
        start_date = None
        end_date = None

        # Select InsightModel
        # Can also filter on ManyToOne objects like this:
        # ih = Insight.objects.filter(user_id=1, channel__official_channel_name='Etsy')
        insight_history = InsightHistorySummary.objects.filter(user_id=account.user_id)
        insight = None
        already_tried = []

        # History for this source to know if this is the first Insight
        count = 0
        if len(insight_history) > 0:
            count = Insight.objects.filter(user_id=account.user_id,
                                           data_provider_id=account.id,
                                           data_provider_name=account.__class__.__name__).count()

        is_initial = (count == 0)

        # Select period and set special params
        if not is_initial:  # Generate the period
            (period, start_date, end_date) = isBeginningOfPeriod()

        if is_initial:  # Initial insight, free of any period and source consideration for now
            period = 'week'
            im_params = {'rolling_window': True,
                         'account': account}
        elif (period is not None):  # Week/Month/Year insight
            week_end = None
            month_end = None
            year_end = None
            if period == 'week':
                week_end = end_date
                month_start, month_end = getPreviousMonth()
                year_start, year_end = getPreviousYear()
            if period == 'month':
                month_end = end_date
                year_start, year_end = getPreviousYear()
            if period == 'year':
                year_end = end_date
            im_params = {'rolling_window': False,
                         'week_end': week_end,
                         'month_start': month_start,
                         'month_end': month_end,
                         'year_start': year_start,
                         'year_end': year_end,
                         'start_date': start_date,
                         'end_date': end_date,
                         'account': account}
        else:
            im_params = {'rolling_window': rolling_window,
                         'account': account}

        all_txns_df = None
        all_txns_for_source_df = None

        while insight is None:
            insight_model = cls.choose_insight_model(account.user_id,
                                                     account.official_channel_name,
                                                     fetched_from_all,
                                                     period,
                                                     insight_history,
                                                     exclude_list=already_tried,
                                                     is_initial=is_initial)
            if insight_model is None:
                return None

            already_tried.append(insight_model)

            # Fetch appropriate txns data
            if insight_model.compares_sources:
                if all_txns_df is None:
                    all_txns_df = curr.convert_common_transactions_df(CTDF.find(user_id=account.user_id),
                                                                      'USD', False)

                if all_txns_df is not None:
                    txns = all_txns_df.copy()
                else:
                    txns = None
            else:
                if all_txns_for_source_df is None:
                    all_txns_for_source_df = curr.convert_common_transactions_df(
                                                             CTDF.find(
                                                                       user_id=account.user_id,
                                                                       data_provider_name=account.__class__.__name__,
                                                                       data_provider_id=account.id),
                                                             'USD', False)

                if all_txns_for_source_df is not None:
                    txns = all_txns_for_source_df.copy()
                else:
                    txns = None

            (insight, channels, products) = insight_model.execute(account.user_id,
                                                                  account.official_channel_name,
                                                                  txns, period, **im_params) or (None, None, None)
            
            logger.info("InsightModel %(insight_model)s resulted in Insight %(insight)s" % 
                        {'insight_model': insight_model,
                         'insight': insight})

        if insight is not None:
            insight.is_initial = is_initial

        return (insight, channels, products)


class TopChannelInsight(InsightModel):
    """
    Given the passed CommonTransactions returns an insight of the form:
    "Your largest channel is %(source)s, making up %(share)s of your revenue."

    If the transactions list is empty return None
    Assumes that currencies are normalized
    """
    def __init__(self, *args, **kwargs):
        super(TopChannelInsight, self).__init__(*args, **kwargs)
        self.periods = None
        self.is_for_initial_pull = False
        self.is_for_update_pull = True
        self.is_limited = False
        self.is_source_limited = False
        self.is_product_limited = False
        self.compares_sources = True
        self.priority = 7
        self.shows_table = False
        self.output_message = "Your largest channel is %(source)s, making up %(share)s of your revenue."

    def execute(self, user_id, source, txns, period, **kwargs):
        from r2d2.insights.models import Insight

        if txns is None or txns.shape[0] == 0:
            return None

        txnsDF = salesByChannel(txns)

        share = txnsDF.share.max()
        source = txnsDF.source[txnsDF.share.idxmax()]

        channels = channels_from_common_transactions_df(txnsDF)
        insight = Insight(insight_model_id=self.type_id,
                          time_period=format_time_period_string(txns.date.min(), txns.date.max()),
                          text=self.output_message %
                          {"source": source,
                           "share": percentTableFormat(share)})

        return(insight, channels, None)


class BestRevenueWeekEverInsight(InsightModel):
    """
    Given the passed CommonTransactions returns an insight of the form:
    "Last week was your biggest ever on %(source)s!  You sold %(total_rev)s, a %(percent_over)s \
    increase over your second best week (the week ending %(second_best_week)s)."

    If the transactions list is empty return None
    Assumes that currencies are normalized
    """
    def __init__(self, *args, **kwargs):
        super(BestRevenueWeekEverInsight, self).__init__(*args, **kwargs)
        self.periods = ['week']
        self.is_for_initial_pull = False
        self.is_for_update_pull = True
        self.is_limited = False
        self.is_source_limited = False
        self.is_product_limited = False
        self.compares_sources = False
        self.priority = 0
        self.shows_table = False
        self.output_message = "Last week was your biggest ever on %(source)s!  You made %(total_rev)s, %(percent_over)s\
         more than your second best week (the week ending %(second_best_week)s)."

    def execute(self, user_id, source, txns, period, **kwargs):
        from r2d2.insights.models import Insight

        if txns is None or txns.shape[0] == 0:
            return None
        elif period not in self.periods:
            return None

        msg = ["Last week was your biggest ever on %(source)s!  You made %(total_rev)s",
               ", %(percent_over)s more than your second best week (the week ending %(second_best_week)s)."]
        week_end = kwargs.get('week_end')

        txnsDF = txns
        channels = channels_from_common_transactions_df(txns)

        grouper = pd.TimeGrouper('1W')
        txnsDF.index = txnsDF.date
        txnsDF = txnsDF.groupby([grouper, 'transaction_id'])
        # Note we can't just sum the total_total_converted column by group because it's denormalized
        txnsDF = txnsDF.first()[['total_total_converted']].groupby(level=0).agg('sum')

        if week_end.date() != txnsDF.total_total_converted.idxmax().date():  # Not your biggest week :(
            return None

        total_rev = txnsDF.total_total_converted.max()

        if total_rev == 0.0:
            return None

        lessers = txnsDF.drop(txnsDF.total_total_converted.idxmax())
        second_best_week = lessers.total_total_converted.idxmax()

        if lessers.total_total_converted.max() != 0.0:
            percent_over = (total_rev/lessers.total_total_converted.max()) - Decimal(1.0)
            output_message = msg[0] + msg[1]
        else:
            percent_over = 0.0
            output_message = msg[0] + '.'

        insight = Insight(insight_model_id=self.type_id,
                          time_period=format_time_period_string(kwargs.get('week_start'), week_end),
                          text=output_message %
                          {"source": source,
                           "total_rev": dollarTableFormat(total_rev),
                           "percent_over": percentTableFormat(percent_over),
                           "second_best_week": periodFormatter(second_best_week, 'week')})

        return(insight, channels, None)


class BestUnitsWeekEverInsight(InsightModel):
    """
    Given the passed CommonTransactions returns an insight of the form:
    "Last week you sold a record number of products on %(source)s!  You sold %(total_units)s, a %(percent_over)s \
    increase over your second best week (the week ending %(second_best_week)s)."

    If the transactions list is empty return None
    """
    def __init__(self, *args, **kwargs):
        super(BestUnitsWeekEverInsight, self).__init__(*args, **kwargs)
        self.periods = ['week']
        self.is_for_initial_pull = False
        self.is_for_update_pull = True
        self.is_limited = False
        self.is_source_limited = False
        self.is_product_limited = False
        self.compares_sources = False
        self.priority = 0
        self.shows_table = False
        self.output_message = "Last week you sold a record number of products on %(source)s!  You sold %(total_units)s,\
         a %(percent_over)s increase over your second best week (the week ending %(second_best_week)s)."

    def execute(self, user_id, source, txns, period, **kwargs):
        from r2d2.insights.models import Insight

        if txns is None or txns.shape[0] == 0:
            return None
        elif period not in self.periods:
            return None

        msg = ["Last week you sold a record number of products on %(source)s!  Sales totaled %(total_units)s units",
               ", a %(percent_over)s increase over your second best week (the week ending %(second_best_week)s)."]

        week_end = kwargs.get('week_end')

        txnsDF = txns
        channels = channels_from_common_transactions_df(txns)

        grouper = pd.TimeGrouper('1W')
        txnsDF.index = txnsDF.date
        txnsDF = txnsDF.groupby(grouper)
        txnsDF = txnsDF.agg({'product_quantity': 'sum'})

        if week_end.date() != txnsDF.product_quantity.idxmax().date():  # Not your biggest week :(
            return None

        total_units = txnsDF.product_quantity.max()

        if total_units == 0.0:
            return None

        lessers = txnsDF.drop(txnsDF.product_quantity.idxmax())
        second_best_week = lessers.product_quantity.idxmax()

        if lessers.product_quantity.max() != 0.0:
            percent_over = (total_units/lessers.product_quantity.max()) - Decimal(1.0)
            output_message = msg[0] + msg[1]
        else:
            percent_over = 0.0
            output_message = msg[0] + '.'

        insight = Insight(insight_model_id=self.type_id,
                          time_period=format_time_period_string(kwargs.get('week_start'), week_end),
                          text=output_message %
                          {"source": source,
                           "total_units": integerTableFormat(total_units),
                           "percent_over": percentTableFormat(percent_over),
                           "second_best_week": periodFormatter(second_best_week, 'week')})

        return(insight, channels, None)


class BestTransactionsWeekEverInsight(InsightModel):
    """
    Given the passed CommonTransactions returns an insight of the form:
    'You completed more transactions on %(source)s last week than ever before!  %(txn_total)s transactions is \
    a %(percent)s increase over the second place week ending %(second_best_week)s'

    If the transactions list is empty return None
    """
    def __init__(self, *args, **kwargs):
        super(BestTransactionsWeekEverInsight, self).__init__(*args, **kwargs)
        self.periods = ['week']
        self.is_for_initial_pull = False
        self.is_for_update_pull = True
        self.is_limited = False
        self.is_source_limited = False
        self.is_product_limited = False
        self.compares_sources = False
        self.priority = 0
        self.shows_table = False
        self.output_message = 'You completed more transactions on %(source)s last week than ever before!\
          %(txn_total)s transactions is a %(percent)s increase over the second place week ending %(second_best_week)s'

    def execute(self, user_id, source, txns, period, **kwargs):
        from r2d2.insights.models import Insight

        if txns is None or txns.shape[0] == 0:
            return None
        elif period not in self.periods:
            return None

        msg = ['You completed more transactions on %(source)s last week than ever before!  \
        %(total_txns)s total transactions',
               ' is a %(percent_over)s increase over the second place week (the week ending %(second_best_week)s).']

        week_end = kwargs.get('week_end')

        txnsDF = txns
        channels = channels_from_common_transactions_df(txns)

        grouper = pd.TimeGrouper('1W')
        txnsDF.index = txnsDF.date
        txnsDF = txnsDF.groupby(grouper)
        txnsDF = txnsDF.agg({'transaction_id': 'count'})

        if week_end.date() != txnsDF.transaction_id.idxmax().date():  # Not your biggest week :(
            return None

        total_txns = txnsDF.transaction_id.max()

        if total_txns == Decimal(0.0):
            return None

        lessers = txnsDF.drop(txnsDF.transaction_id.idxmax())
        second_best_week = lessers.transaction_id.idxmax()

        if lessers.transaction_id.max() != Decimal(0.0):
            percent_over = (Decimal(total_txns)/Decimal(lessers.transaction_id.max())) - Decimal(1.0)
            output_message = msg[0] + msg[1]
        else:
            percent_over = 0.0
            output_message = msg[0] + '.'

        insight = Insight(insight_model_id=self.type_id,
                          time_period=format_time_period_string(kwargs.get('week_start'), week_end),
                          text=output_message %
                          {"source": source,
                           "total_txns": integerTableFormat(total_txns),
                           "percent_over": percentTableFormat(percent_over),
                           "second_best_week": periodFormatter(second_best_week, 'week')})

        return(insight, channels, None)


class PeriodProductComparisonInsight(InsightModel):
    """
    Given the passed CommonTransactions returns an insight of the form:

    'You sold %(week_quantity)s total %(product)s this week, %(month_quantity)s this month, \
    and %(year_quantity)s this year.'

    rolling_window:  whether to use the last available period (week, month, year) rather than a period fixed to a
        calendar week, calendar month, or calendar year.  If False week_end, month_end, and year_end should be passed.
    week_end:  the final day of the week to use for period comparisons
    month_end:  the final day of the month to use for period comparisons
    year_end:  the final day of the year to use for period comparisons

    returns None if:
    - the transaction list is empty
    - week_end is not present in the passed transactions
    - no product was sold in all three of the last week, month, and year

    TODO:  this insight would be great to kick out a different product each time
    """
    def __init__(self, *args, **kwargs):
        super(PeriodProductComparisonInsight, self).__init__(*args, **kwargs)
        self.periods = ['week']
        self.is_for_initial_pull = True
        self.is_for_update_pull = True
        self.is_limited = False
        self.is_source_limited = False
        self.is_product_limited = True
        self.compares_sources = False
        self.priority = 3
        self.shows_table = False
        self.output_message = 'You sold %(week_quantity)s total %(product)s in your last sales week, %(month_quantity)s\
         in your last sales month, and %(year_quantity)s in your last sales year.'

    def execute(self, user_id, source, txns, period, **kwargs):
        from r2d2.insights.models import Insight, Product

        if txns is None or txns.shape[0] == 0:
            return None

        rolling_window = kwargs.get('rolling_window', True)
        week_end = kwargs.get('week_end')
        month_end = kwargs.get('month_end')
        year_end = kwargs.get('year_end')

        txnsDF = txns

        if (rolling_window is False):
            byWeek = salesByPeriod(txnsDF, 'week', True)
            time_period = format_time_period_string(kwargs.get('week_start'), week_end)
        elif (rolling_window is True):
            byWeek = salesByPeriod(txnsDF, '7 days', True)
            time_period = format_time_period_string(txnsDF.date.max() - timedelta(days=7), txnsDF.date.max())

        if (rolling_window is False and week_end not in byWeek.index):
            return None
        elif (rolling_window is True):
            byMonth = salesByPeriod(txnsDF, '30 days', True)
            byYear = salesByPeriod(txnsDF, '365 days', True)
            week_end = max(byWeek.index.get_level_values(0))  # Retrieves the final timestamp
            product = byWeek.loc[week_end, ].index[0][0]
            sku = byWeek.loc[week_end, ].index[0][1]
            week_quantity = byWeek.loc[(week_end, product, sku)].product_quantity
            month_quantity = byMonth.loc[(max(byMonth.index.get_level_values(0)), product, sku)].product_quantity
            year_quantity = byYear.loc[(max(byYear.index.get_level_values(0)), product, sku)].product_quantity
            time_period = format_time_period_string(txnsDF.date.max() - timedelta(days=365), txnsDF.date.max())
        else:
            byMonth = salesByPeriod(txnsDF, 'month', True)
            byYear = salesByPeriod(txnsDF, 'year', True)
            time_period = format_time_period_string(kwargs.get('year_start'), year_end)

            # choose which product
            for (oneProduct, oneSku) in byWeek.loc[week_end, ].index:
                if (month_end, oneProduct, oneSku) in byMonth.index:
                    if (year_end, oneProduct, oneSku) in byYear.index:
                        week_quantity = byWeek.loc[week_end].loc[oneProduct].loc[oneSku].product_quantity
                        month_quantity = byMonth.loc[month_end].loc[oneProduct].loc[oneSku].product_quantity
                        year_quantity = byYear.loc[year_end].loc[oneProduct].loc[oneSku].product_quantity
                        product = oneProduct
                        sku = oneSku
                        break
                else:
                    return None

        product = Product(name=product, sku=sku)
        insight = Insight(insight_model_id=self.type_id,
                          time_period=time_period,
                          text=self.output_message %
                          {"week_quantity": integerTableFormat(week_quantity),
                           "month_quantity": integerTableFormat(month_quantity),
                           "year_quantity": integerTableFormat(year_quantity),
                           "product": product.name})

        return(insight, None, [product])


class TopPeriodInsight(InsightModel):
    """
    Given the passed CommonTransactions returns an insight of the form:
    "Your biggest %(period)s on %(source)s was %(periodStr)s.  You sold over %(maxTotal)s"

    If the transactions list is empty or the period is not recognized it returns None
    TODO:  should period just be the frequency offset from
    http://pandas.pydata.org/pandas-docs/stable/timeseries.html#offset-aliases?
    """
    def __init__(self, *args, **kwargs):
        super(TopPeriodInsight, self).__init__(*args, **kwargs)
        # periods insight should be used for period analysis: 'year', 'month', 'week', or empty list
        self.periods = ['year', 'month', 'week', 'quarter']
        self.is_for_initial_pull = True  # whether Insight should be used for the initial transaction pull
        self.is_for_update_pull = False  # whether Insight should be used for transaction updates
        self.is_limited = False  # whether Insight should not be used repeatedly
        self.is_source_limited = True  # whether Insight should not be used repeatedly for the same source
        self.is_product_limited = False  # whether Insight should not be used repeatedly for the same product
        self.compares_sources = False
        self.priority = 2  # the relative importance of this Insight
        self.shows_table = False  # whether this insight shows a table
        self.output_message = "Your biggest %(period)s on %(source)s was %(periodStr)s.  You sold over %(maxTotal)s"

    def execute(self, user_id, source, txns, period, **kwargs):
        from r2d2.insights.models import Insight
        if txns is None or txns.shape[0] == 0:
            return None

        channels = channels_from_common_transactions_df(txns)
        txnsDF = salesByPeriod(txns, period)

        maxTotal = txnsDF.product_total_converted.max()
        topPeriod = txnsDF.product_total_converted.idxmax()

        start_date = kwargs.get('start_date')
        end_date = kwargs.get('end_date')

        if start_date is None:
            start_date = txns.date.min()

        if end_date is None:
            end_date = txns.date.max()

        time_period = format_time_period_string(start_date, end_date)

        if (period == 'week'):
            periodStr = 'the week ending %(topPeriod)s' % {"topPeriod": periodFormatter(topPeriod, 'day')}
        elif (period == 'quarter'):
            periodStr = 'the quarter ending %(topPeriod)s' % {"topPeriod": periodFormatter(topPeriod, 'day')}
            time_period = format_time_period_string(kwargs.get('quarter_start'), kwargs.get('quarter_end'))
        else:
            periodStr = periodFormatter(topPeriod, period)
            time_period = format_time_period_string(kwargs.get('year_start'), kwargs.get('year_end'))

        insight = Insight(insight_model_id=self.type_id,
                          time_period=time_period,
                          text=self.output_message %
                          {"source": source,
                           "period": period,
                           "periodStr": periodStr,
                           "maxTotal": dollarTableFormat(maxTotal)})
        return(insight, channels, None)


class SalesByChannelInsight(InsightModel):
    """
    Returns an insight for sales and quantities grouped by channel
    of the form:
    'Here\'s last %(period)s\'s sales breakdown<br><br> %(table)s '

    If the transactions list is empty return None
    """
    def __init__(self, *args, **kwargs):
        super(SalesByChannelInsight, self).__init__(*args, **kwargs)
        self.periods = ['year', 'month', 'week', 'quarter']
        self.is_for_initial_pull = False
        self.is_for_update_pull = True
        self.is_limited = False
        self.is_source_limited = False
        self.is_product_limited = False
        self.compares_sources = True
        self.priority = 1
        self.shows_table = True
        self.output_message = 'Here\'s last %(period)s\'s sales breakdown<br><br> %(table)s '

    def execute(self, user_id, source, txns, period, **kwargs):
        from r2d2.insights.models import Insight

        if txns is None or txns.shape[0] == 0:
            return None

        txnsDF = salesByChannel(txns)
        channels = channels_from_common_transactions_df(txnsDF)

        txnsDF = normalizeDFColumns(txnsDF)
        txnsDF = txnsDF[['Channel', 'Item Quantity', 'Item Total', 'Share']]
        txnsDF = txnsDF.set_index(['Channel'])
        txnsDF.index.name = None
        tableStr = dfToHTML(txnsDF)

        insight = Insight(insight_model_id=self.type_id,
                          time_period=format_time_period_string(txns.date.min(), txns.date.max()),
                          text=self.output_message %
                          {'period': period,
                           'table': tableStr})
        return(insight, channels, None)


class DiscountPercentageInsight(InsightModel):
    """
    Returns an insight indicating total percentage of sales discounted in the
    previous day:
    '%(percentage)s of your sales on %(source)s were discounted yesterday'

    If the transactions list is empty return None
    """
    def __init__(self, *args, **kwargs):
        super(DiscountPercentageInsight, self).__init__(*args, **kwargs)
        self.periods = None
        self.is_for_initial_pull = False
        self.is_for_update_pull = True
        self.is_limited = False
        self.is_source_limited = False
        self.is_product_limited = False
        self.compares_sources = False
        self.priority = 5
        self.shows_table = False
        self.output_message = '%(percentage)s of your sales on %(source)s were discounted yesterday'

    def execute(self, user_id, source, txns, period, **kwargs):
        from r2d2.insights.models import Insight

        if txns is None or txns.shape[0] == 0:
            return None

        txnsDF = txns

        account = kwargs['account']
        end_date = account.last_successfull_call
        start_date = end_date - timedelta(days=1)

        txnsDF = txnsDF.loc[(txnsDF['date'] >= start_date) & (txnsDF['date'] <= end_date)]

        if txnsDF is None:
            return None

        channels = channels_from_common_transactions_df(txnsDF)

        # Note we can't just sum the total_total_converted column by group because it's denormalized
        txnsDF = txnsDF.groupby(['transaction_id'])
        txnsDF = txnsDF.first()[['total_total_converted', 'total_discount_converted']]

        if txnsDF.total_total_converted.sum() != 0:
            discount_share = abs(txnsDF.total_discount_converted.sum()/txnsDF.total_total_converted.sum())
        else:
            return None

        if txnsDF.total_discount_converted.sum() == 0:
            message = "No sales were discounted on %(source)s yesterday"
        else:
            message = self.output_message

        insight = Insight(insight_model_id=self.type_id,
                          time_period=format_time_period_string(end_date),
                          text=message %
                          {'source': source,
                           'percentage': percentTableFormat(discount_share)})
        return(insight, channels, None)


class DailyAverageProductsPerTransaction(InsightModel):
    """
    Returns an insight indicating average number of products per transaction for
    in the previous day:
    'You averaged %(average)s products per transaction yesterday'

    If the transactions list is empty return None
    """
    def __init__(self, *args, **kwargs):
        super(DailyAverageProductsPerTransaction, self).__init__(*args, **kwargs)
        self.periods = None
        self.is_for_initial_pull = False
        self.is_for_update_pull = True
        self.is_limited = False
        self.is_source_limited = False
        self.is_product_limited = False
        self.compares_sources = False
        self.priority = 5
        self.shows_table = False
        self.output_message = 'You averaged %(average)s products per transaction yesterday on %(source)s'

    def execute(self, user_id, source, txns, period, **kwargs):
        from r2d2.insights.models import Insight

        if txns is None or txns.shape[0] == 0:
            return None

        txnsDF = txns

        account = kwargs['account']
        end_date = account.last_successfull_call
        start_date = end_date - timedelta(days=1)

        txnsDF = txnsDF.loc[(txnsDF['date'] >= start_date) & (txnsDF['date'] <= end_date)]

        if txns is None or txns.shape[0] == 0:
            return None

        channels = channels_from_common_transactions_df(txnsDF)
        txnsDF = txnsDF.groupby(['transaction_id'])
        txnsDF = txnsDF.agg({'product_name': 'count'})
        average = txnsDF.product_name.mean()

        if math.isnan(average):
            return None

        insight = Insight(insight_model_id=self.type_id,
                          time_period=format_time_period_string(end_date),
                          text=self.output_message %
                          {'source': source,
                           'average': decimalNumberFormat(average)})
        return(insight, channels, None)


class WeeklyAverageProductsPerTransaction(InsightModel):
    """
    Returns an insight indicating average number of products per transaction for
    in the previous week:
    'You averaged %(average)s products per transaction last week'

    If the transactions list is empty return None
    """
    def __init__(self, *args, **kwargs):
        super(WeeklyAverageProductsPerTransaction, self).__init__(*args, **kwargs)
        self.periods = ['week']
        self.is_for_initial_pull = False
        self.is_for_update_pull = True
        self.is_limited = False
        self.is_source_limited = False
        self.is_product_limited = False
        self.compares_sources = False
        self.priority = 7
        self.shows_table = False
        self.output_message = 'Last week you averaged %(average)s products per transaction on %(source)s'

    def execute(self, user_id, source, txns, period, **kwargs):
        from r2d2.insights.models import Insight

        if txns is None or txns.shape[0] == 0:
            return None

        end_date = kwargs['end_date']
        start_date = kwargs['start_date']

        txnsDF = txns.loc[(txns['date'] >= start_date) & (txns['date'] <= end_date)]

        if txnsDF is None or txnsDF.shape[0] == 0:
            return None

        channels = channels_from_common_transactions_df(txnsDF)

        txnsDF = txnsDF.groupby(['transaction_id'])
        txnsDF = txnsDF.agg({'product_name': 'count'})
        average = txnsDF.product_name.mean()

        if math.isnan(average):
            return None

        insight = Insight(insight_model_id=self.type_id,
                          time_period=format_time_period_string(start_date, end_date),
                          text=self.output_message %
                          {'source': source,
                           'average': decimalNumberFormat(average)})
        return(insight, channels, None)


class AverageTransactionsPerPeriodInsight(InsightModel):
    """
    Returns an insight indicating average number of transaction per period and
    compares this to the same period in the previous timeframe (e.g. December of
    the previous year; previous year)

    'You averaged %(average)s transactions per week last month.  This is %(percent)s
    %(more_or_less)s than the same month last year'

    and

    'You averaged %(average)s transactions per week last year.  This is %(percent)s
    %(more_or_less)s than the previous year'

    If the transactions list is empty return None
    """
    def __init__(self, *args, **kwargs):
        super(AverageTransactionsPerPeriodInsight, self).__init__(*args, **kwargs)
        self.periods = ['month', 'year']
        self.is_for_initial_pull = False
        self.is_for_update_pull = True
        self.is_limited = False
        self.is_source_limited = False
        self.is_product_limited = False
        self.compares_sources = False
        self.priority = 4
        self.shows_table = False
        self.output_message = 'You averaged %(current_average)s transactions per week last month.  \
        This is %(percent_diff)s %(more_or_less)s than the previous month'

    def execute(self, user_id, source, txns, period, **kwargs):
        from r2d2.insights.models import Insight

        if txns is None or txns.shape[0] == 0:
            return None
        elif period not in self.periods:
            return None

        txnsDF = txns

        end_date = kwargs['end_date']
        start_date = kwargs['start_date']

        this_period_txns = txnsDF.loc[(txnsDF['date'] >= start_date) & (txnsDF['date'] <= end_date)]

        if this_period_txns is None or this_period_txns.shape[0] == 0:
            return None

        channels = channels_from_common_transactions_df(txnsDF)

        grouper = pd.TimeGrouper('1W')
        this_period_txns.index = this_period_txns.date
        this_period_txns = this_period_txns.groupby(grouper)
        this_period_txns = this_period_txns.agg({'transaction_id': 'count'})
        current_average = this_period_txns.transaction_id.mean()

        if math.isnan(current_average):
            return None

        if period == 'month':
            msg = ['You averaged %(current_average)s transactions per week last month on %(source)s.',
                   '  This is %(percent_diff)s %(more_or_less)s than the previous month.']
            (start_date, end_date) = getPreviousMonth(start_date)
        else:
            msg = ['You averaged %(current_average)s transactions per week last year on %(source)s.',
                   '  This is %(percent_diff)s %(more_or_less)s than the previous year']
            (start_date, end_date) = getPreviousYear(start_date)

        last_period_txns = txnsDF.loc[(txnsDF['date'] >= start_date) & (txnsDF['date'] <= end_date)]

        # If no txns in previous period then don't include the second sentence in the output
        if last_period_txns.shape[0] == 0:
            msg[1] = ''
            percent_diff = 0.0
            more_or_less = ''
        else:
            last_period_txns.index = last_period_txns.date
            last_period_txns = last_period_txns.groupby(grouper)
            last_period_txns = last_period_txns.agg({'transaction_id': 'count'})
            previous_average = last_period_txns.transaction_id.mean()

            if math.isnan(previous_average) or previous_average == 0.0:
                msg[1] = ''
            else:
                percent_diff = current_average / previous_average

                if percent_diff < 1.0:
                    more_or_less = 'less'
                    percent_diff = 1.0 - percent_diff
                elif percent_diff > 1.0:
                    more_or_less = 'more'
                    percent_diff = percent_diff - 1.0
                else:
                    if period == 'month':
                        msg[1] = '  This is the same as the previous month'
                    else:
                        msg[1] = '  This is the same as the previous year'

        output_message = msg[0] + msg[1]
        insight = Insight(insight_model_id=self.type_id,
                          time_period=format_time_period_string(start_date, end_date),
                          text=output_message %
                          {'source': source,
                           'current_average': decimalNumberFormat(current_average),
                           'percent_diff': percentTableFormat(percent_diff),
                           'more_or_less': more_or_less})
        return(insight, channels, None)


class TopProductsInsight(InsightModel):
    """
    Returns an insight for sales and quantities grouped by product
    of the form:
    'Here\'s last %(period)s\'s sales breakdown<br><br> %(table)s '

    If the transactions list is empty return None
    """
    def __init__(self, *args, **kwargs):
        super(TopProductsInsight, self).__init__(*args, **kwargs)
        self.periods = ['year', 'month', 'week', 'quarter']
        self.is_for_initial_pull = False
        self.is_for_update_pull = True
        self.is_limited = False
        self.is_source_limited = False
        self.is_product_limited = False
        self.compares_sources = False
        self.priority = 2
        self.shows_table = True
        self.output_message = 'Here\'s last %(period)s\'s sales breakdown<br><br> %(table)s '

    def execute(self, user_id, source, txns, period, **kwargs):
        from r2d2.insights.models import Insight

        if txns is None or txns.shape[0] == 0:
            return None

        start_date = kwargs['start_date']
        end_date = kwargs['end_date']

        channels = channels_from_common_transactions_df(txns)
        txnsDF = topProducts(txns, start_date, end_date)

        if txnsDF is None or txnsDF.shape[0] == 0:
            return None

        txnsDF = normalizeDFColumns(txnsDF)
        txnsDF = txnsDF[['Name', 'Item Quantity', 'Item Total']]
        txnsDF = txnsDF.set_index(['Name'])
        txnsDF.index.name = None
        tableStr = dfToHTML(txnsDF, True)

        insight = Insight(insight_model_id=self.type_id,
                          time_period=format_time_period_string(start_date, end_date),
                          text=self.output_message %
                          {"period": period,
                           "table": tableStr})
        return(insight, channels, None)


class DailyProductSalesInsight(InsightModel):
    """
    Returns an insight for sales and quantities over the previous day,
    grouped by product of the form:
    'Here\'s yesterday's sales breakdown<br><br> %(table)s '

    If the transactions list is empty return None
    """
    def __init__(self, *args, **kwargs):
        super(DailyProductSalesInsight, self).__init__(*args, **kwargs)
        self.periods = None
        self.is_for_initial_pull = False
        self.is_for_update_pull = True
        self.is_limited = False
        self.is_source_limited = False
        self.is_product_limited = False
        self.compares_sources = False
        self.priority = 10
        self.shows_table = True
        self.output_message = 'Here\'s yesterday\'s sales breakdown for %(source)s<br><br> %(table)s '

    def execute(self, user_id, source, txns, period, **kwargs):
        from r2d2.insights.models import Insight

        if txns is None or txns.shape[0] == 0:
            return None

        txnsDF = txns

        account = kwargs['account']
        end_date = account.last_successfull_call
        start_date = end_date - timedelta(days=1)

        txnsDF = txnsDF.loc[(txnsDF['date'] >= start_date) & (txnsDF['date'] <= end_date)]

        if txnsDF is None or txnsDF.shape[0] == 0:
            return None

        channels = channels_from_common_transactions_df(txnsDF)

        txnsDF = txnsDF.groupby(['product_name'])
        txnsDF = txnsDF.agg({'product_quantity': 'sum', 'product_total_converted': 'sum'})

        txnsDF = normalizeDFColumns(txnsDF)
        txnsDF = txnsDF[['Item Quantity', 'Item Total']]
        txnsDF.index.name = None
        tableStr = dfToHTML(txnsDF, True)

        insight = Insight(insight_model_id=self.type_id,
                          time_period=format_time_period_string(end_date),
                          text=self.output_message %
                          {"source": source,
                           "table": tableStr})
        return(insight, channels, None)


class BestSellingProductsInsight(InsightModel):
    """
    Returns an insight with a list of the top 1-3 products (by quantity)
    of the form:
    'Your best selling products:
    * product 1
    * product 2
    * product 3'

    If the transactions list is empty return None
    """
    def __init__(self, *args, **kwargs):
        super(BestSellingProductsInsight, self).__init__(*args, **kwargs)
        self.periods = None
        self.is_for_initial_pull = True
        self.is_for_update_pull = True
        self.is_limited = False
        self.is_source_limited = False
        self.is_product_limited = False
        self.compares_sources = False
        self.priority = 6
        self.shows_table = False
        self.output_message = 'Your best selling products on %(source)s:<br>%(product_table)s'

    def execute(self, user_id, source, txns, period, **kwargs):
        from r2d2.insights.models import Insight
        if txns is None or txns.shape[0] == 0:
            return None

        channels = channels_from_common_transactions_df(txns)
        txnsDF = topProducts(txns, None, None)

        if txnsDF is None or txnsDF.shape[0] == 0:
            return None

        txnsDF = txnsDF.sort_values(by=['product_quantity'], ascending=False)
        productsList = txnsDF.product_name[0:3].tolist()
        product_table = listToHTML(productsList)

        insight = Insight(insight_model_id=self.type_id,
                          time_period=format_time_period_string(txns.date.min(), txns.date.max()),
                          text=self.output_message %
                          {"source": source,
                           "product_table": product_table})
        return(insight, channels, None)


class ProductCountInsight(InsightModel):
    """
    Returns an insight telling how many individual products have been sold:

    'You\'ve sold %(products)s unique products over the last %(timeframe)s'

    If the transactions list is empty return None
    """
    def __init__(self, *args, **kwargs):
        super(ProductCountInsight, self).__init__(*args, **kwargs)
        self.periods = None
        self.is_for_initial_pull = True
        self.is_for_update_pull = True
        self.is_limited = False
        self.is_source_limited = False
        self.is_product_limited = False
        self.compares_sources = True
        self.priority = 6
        self.shows_table = False
        self.output_message = 'You\'ve sold %(products)s unique products over the last %(timeframe)s'

    def execute(self, user_id, source, txns, period, **kwargs):
        from r2d2.insights.models import Insight
        if txns is None or txns.shape[0] == 0:
            return None

        channels = channels_from_common_transactions_df(txns)
        txnsDF = txns

        products = txnsDF.product_name.unique().size
        timeframe = txnsDF.date.min()

        insight = Insight(insight_model_id=self.type_id,
                          time_period=format_time_period_string(timeframe, kwargs.get('end_date')),
                          text=self.output_message %
                          {"products": products,
                           "timeframe": fancyDateTimeDeltaFormat(timeframe, levels=2)})
        return(insight, channels, None)


class OldestTransactionInsight(InsightModel):
    """
    Returns an insight telling when the oldest transaction on a channel was

    'Your first transaction on %(source)s was way back on %(date)s:<br>%(txns_detail)s'

    If the transactions list is empty return None
    """
    def __init__(self, *args, **kwargs):
        super(OldestTransactionInsight, self).__init__(*args, **kwargs)
        self.periods = None
        self.is_for_initial_pull = False
        self.is_for_update_pull = True
        self.is_limited = False
        self.is_source_limited = True
        self.is_product_limited = False
        self.compares_sources = False
        self.priority = 10
        self.shows_table = True
        self.output_message = 'Your first transaction on %(source)s was way back on %(date)s:<br><br>%(txn_detail)s'

    def execute(self, user_id, source, txns, period, **kwargs):
        from r2d2.insights.models import Insight
        if txns is None or txns.shape[0] == 0:
            return None

        txnsDF = txns

        end_date = kwargs.get('end_date')

        if end_date is None:
            end_date = txnsDF.date.max()

        date = txnsDF.date.min()

        txnsDF = txnsDF[txnsDF.date == date]
        channels = channels_from_common_transactions_df(txnsDF)
        txnsDF = topProducts(txnsDF)
        txnsDF = normalizeDFColumns(txnsDF)
        txnsDF = txnsDF[['Name', 'Item Quantity', 'Item Total']]
        txnsDF = txnsDF.set_index(['Name'])
        txnsDF.index.name = None
        tableStr = dfToHTML(txnsDF)

        insight = Insight(insight_model_id=self.type_id,
                          time_period=format_time_period_string(end_date),
                          text=self.output_message %
                          {"source": source,
                           "date": periodFormatter(date, "day"),
                           "txn_detail": tableStr})
        return(insight, channels, None)


class DaysSinceLastTransactionInsight(InsightModel):
    """
    Returns an insight telling when the last transaction on a channel was

    'Your last sale on %(source)s was %(time_period)s ago'

    If the transactions list is empty return None
    """
    def __init__(self, *args, **kwargs):
        super(DaysSinceLastTransactionInsight, self).__init__(*args, **kwargs)
        self.periods = None
        self.is_for_initial_pull = False
        self.is_for_update_pull = True
        self.is_limited = False
        self.is_source_limited = True
        self.is_product_limited = False
        self.compares_sources = False
        self.priority = 10
        self.shows_table = False
        self.output_message = 'Your last sale on %(source)s was %(time_period)s ago'

    def execute(self, user_id, source, txns, period, **kwargs):
        from r2d2.insights.models import Insight
        if txns is None or txns.shape[0] == 0:
            return None

        end_date = datetime.now()
        date = txns.date.max()
        channels = channels_from_common_transactions_df(txns)

        insight = Insight(insight_model_id=self.type_id,
                          time_period=format_time_period_string(end_date),
                          text=self.output_message %
                          {"source": source,
                           "time_period": fancyDateTimeDeltaFormat(date)})
        return(insight, channels, None)


class ProductMultiplesInsight(InsightModel):
    """
    Returns an insight that determines if certain products are purchased in larger
    quantities (i.e. mode(quantity) > 1)

    'We found that these products are more often purchased in larger quantities on %(source)s:<br><br>%(products)s'

    If the transactions list is empty return None
    """
    def __init__(self, *args, **kwargs):
        super(ProductMultiplesInsight, self).__init__(*args, **kwargs)
        self.periods = None
        self.is_for_initial_pull = False
        self.is_for_update_pull = True
        self.is_limited = False
        self.is_source_limited = False
        self.is_product_limited = False
        self.compares_sources = False
        self.priority = 1
        self.shows_table = True
        self.output_message = 'We found that these products are more often purchased in larger quantities on %(source)s:\
        <br><br>%(products)s'

    def execute(self, user_id, source, txns, period, **kwargs):
        from r2d2.insights.models import Insight
        if txns is None or txns.shape[0] == 0:
            return None

        txnsDF = txns
        channels = channels_from_common_transactions_df(txnsDF)

        start_date = kwargs.get('start_date')
        end_date = kwargs.get('end_date')

        if start_date is None:
            start_date = txnsDF.date.min()

        if end_date is None:
            end_date = txnsDF.date.max()

        txnsDF = txnsDF[['transaction_id', 'product_name', 'product_quantity']]  # take only columns we need
        txnsDF.product_quantity = txnsDF.product_quantity.astype(int)  # convert Decimal to int type
        # don't want to deal with the multiindex but need to group
        dfgrouped = txnsDF.groupby(['transaction_id', 'product_name'], as_index=False)
        # sum product_quantities in each group in case multiple of the same item are listed individually
        txnsDF = dfgrouped.agg('sum')
        txnsDF = mode(txnsDF, ['product_name'], txnsDF.product_quantity, 'count')
        txnsDF = txnsDF[txnsDF.product_quantity > 1]

        if txnsDF.shape[0] == 0:  # no results
            return None

        txnsDF = normalizeDFColumns(txnsDF)
        txnsDF = txnsDF[['Name', 'Item Quantity']]
        txnsDF = txnsDF.set_index(['Name'])
        txnsDF.rename({'Item Quantity': 'Most Frequent Quantity'})
        txnsDF.index.name = None
        tableStr = dfToHTML(txnsDF)

        insight = Insight(insight_model_id=self.type_id,
                          time_period=format_time_period_string(start_date, end_date),
                          text=self.output_message %
                          {"source": source,
                           "products": tableStr})
        return(insight, channels, None)


def salesByChannel(txnsDF):
    """
    Returns a DataFrame of sales and quantities grouped by channel
    If the transactions list is empty return None
    """
    if txnsDF is None or txnsDF.shape[0] == 0:
        return None

    txnsDF = txnsDF.groupby(['source', 'data_provider_name', 'data_provider_id'], as_index=False)
    txnsDF = txnsDF.agg({'product_quantity': 'sum', 'product_total_converted': 'sum'})
    total = txnsDF.product_total_converted.sum()

    if total == 0:
        txnsDF['share'] = 0
    else:
        txnsDF['share'] = txnsDF.product_total_converted/total

    txnsDF = txnsDF.sort_values(by=['share', 'source'], ascending=False)

    return txnsDF


def salesByPeriod(txns, period, by_product=False):
    """
    Returns a DataFrame of sales and quantities grouped by period
    If the transactions list is empty or the period is not recognized it returns None.
    Possible periods:
    year:    by calendar year
    quarter:    by calendar quarter
    month:    by calendar month
    7 days:    chunked into 7-day periods (not necessarily cut on the calendar week)
    30 days:    chunked into 30-day periods (not necessarily cut on the calendar month)
    365 days:    chunked into 365-day periods (not necessarily cut on the calendar year)
    week:    by calendar week
    day:    by calendar day, on natural day breaks
    hour:    by hour, on the hour
    by_product: if True groups by product_name and product_sku.  Defaults to False

    TODO:  should period just be the frequency offset from
    http://pandas.pydata.org/pandas-docs/stable/timeseries.html#offset-aliases?
    """
    if txns is None or txns.shape[0] == 0:
        return None

    if period == 'year':
        freq = '1A'
    elif period == 'quarter':
        freq = '1Q'
    elif period == 'month':
        freq = '1M'
    elif period == '7 days':
        freq = '7D'
    elif period == '30 days':
        freq = '30D'
    elif period == '365 days':
        freq = '365D'
    elif period == 'week':
        freq = '1W'
        # Note we can specify which day the week ends on to pandas with (here week ends on Monday):
        # freq = pandas.tseries.offsets.Week(weekday=0)
        # see: http://pandas.pydata.org/pandas-docs/stable/timeseries.html#dateoffset-objects
    elif period == 'day':
        freq = '1D'
    elif period == 'hour':
        freq = '1H'
    else:
        return None

    # Group by date frequency and by product if needed
    grouper = pd.TimeGrouper(freq)
    txns.index = txns.date

    if (by_product):
        txns = txns.groupby([grouper, 'product_name', 'product_sku'])
    else:
        txns = txns.groupby(grouper)

    # Aggregate
    txns = txns.agg({'product_quantity': 'sum', 'product_total_converted': 'sum'})

    return txns


def topProducts(txnsDF, start_date=None, end_date=None):
    """
    Takes a list of CommonTransaction objects, returns an HTML table of
    products with quantity and totals summed
    """
    if txnsDF is None or txnsDF.shape[0] == 0:
        return None

    if start_date is not None and end_date is not None:
        txnsDF = txnsDF.loc[(txnsDF['date'] >= start_date) & (txnsDF['date'] <= end_date)]

    if txnsDF.shape[0] == 0:
        return None

    txnsDF = txnsDF.groupby(['product_name'], as_index=False)
    txnsDF = txnsDF.agg({'product_quantity': 'sum', 'product_total_converted': 'sum'})
    txnsDF = txnsDF.sort_values(by=['product_total_converted', 'product_quantity'], ascending=False)

    return txnsDF


def normalizeDFColumns(df):
    """
    Replaces column names in the passed pandas.DataFrame with final labels
    """
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

    return df.rename(columns=columnDict)


def dfToHTML(df, withSummary=False):
    """
    Formats the passed pandas.DataFrame to HTML table output
    """
    formatDict = {'Total Price': dollarTableFormat,
                  'Tax': dollarTableFormat,
                  'Discount': dollarTableFormat,
                  'Total': dollarTableFormat,
                  'Price': dollarTableFormat,
                  'Item Quantity': integerTableFormat,
                  'Item Tax': dollarTableFormat,
                  'Item Discount': dollarTableFormat,
                  'Item Total': dollarTableFormat,
                  'Share': percentTableFormat,
                  'total_price': dollarTableFormat,
                  'total_tax': dollarTableFormat,
                  'total_discount': dollarTableFormat,
                  'total_total': dollarTableFormat,
                  'product_quantity': integerTableFormat,
                  'product_price': dollarTableFormat,
                  'product_tax': dollarTableFormat,
                  'product_discount': dollarTableFormat,
                  'product_total': dollarTableFormat,
                  'share': percentTableFormat,
                  'total_price_converted': dollarTableFormat,
                  'total_tax_converted': dollarTableFormat,
                  'total_discount_converted': dollarTableFormat,
                  'total_total_converted': dollarTableFormat,
                  'product_price_converted': dollarTableFormat,
                  'product_tax_converted': dollarTableFormat,
                  'product_discount_converted': dollarTableFormat,
                  'product_total_converted': dollarTableFormat,
                  'value': dollarTableFormat}

    if withSummary:
        df = summary(df)

    return df.to_html(bold_rows=True, index=True, index_names=False, formatters=formatDict)


def listToHTML(a_list, ordered=False):
    """
    Turns the passed list into an HTML list.

    list: the list of items to turn into an HTML list
    ordered:  whether to create an ordered HTML list.  Defaults to False
    """
    if ordered:
        listStr = "<ol>"
    else:
        listStr = "<ul>"

    for an_item in a_list:
        listStr += '<li>' + an_item + '</li>'

    if ordered:
        listStr += "</ol>"
    else:
        listStr += "</ul>"

    return listStr


def summary(df, fn=np.sum, axis=0, name='Total',  table_class_prefix='dataframe-summary'):
    """Append a summary row or column to DataFrame.

    Input:
    ------
    df : DataFrame to be summarized
    fn : Summary function applied over each column
    axis : Axis to summarize on (1: by row, 0: by column)
    name : Index or column label for summary
    table_class_prefix : Custom css class for dataframe

    Returns:
    --------
    DataFrame with applied summary.

    From:  http://blog.henryhhammond.com/pandas-formatting-snippets/#addingasummaryrowcolumn

    """
    total = df.apply(fn, axis=axis).to_frame(name)

    table_class = ""

    if axis == 0:
        total = total.T
        table_class = "{}-row".format(table_class_prefix)
    elif axis == 1:
        table_class = "{}-col".format(table_class_prefix)

    out = pd.concat([df, total], axis=axis)

    # Patch to_html function to use custom css class
    out.to_html = partial(out.to_html, classes=table_class)

    return out


def isBeginningOfPeriod(now=datetime.now()):
    """
    Returns a tuple of (period, period start date, period end date) if passed
    date coincides with the beginning of a week, month, or year.

    - period: "week", "month", "year" if the passed date is at the beginning of
    one of those periods, otherwise None.  For conflicts the period preference
    is: year, month, day.  now defaults to today if not specified
    - start date: the start date of the period if period is not None
    - end date: the end date of the period if period is not None

    TODO:  i18n to fit merchant's locale
    """
    if now.day == 1:  # Beginning of the month or year
        if now.month == 1:  # Beginning of the year
            (first, last) = getPreviousYear(now)
            return ('year', first, last)
        else:  # Beginning of the month
            # Note: doesn't expect to be run in January so it doesn't change the year
            (first, last) = getPreviousMonth(now)
            return ('month', first, last)
    elif now.weekday() == 0:  # Monday, beginning of the week
        (first, last) = getPreviousWeek(now)
        return ('week', first, last)

    return (None, None, None)


def getPreviousYear(fromDate=datetime.now()):
    """
    Returns a tuple of (startDate, endDate) for the min and max datetimes of the
    year previous to fromDate
    """
    firstDay = fromDate.replace(year=fromDate.year-1, month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
    lastDay = firstDay.replace(month=12, day=31, hour=23, minute=59, second=59, microsecond=999999)
    return (firstDay, lastDay)


def getPreviousMonth(fromDate=datetime.now()):
    """
    Returns a tuple of (startDate, endDate) for the min and max datetimes of the
    month previous to fromDate.
    """
    if fromDate.month == 1:  # must handle January to December of prev year move
        firstDay = fromDate.replace(year=fromDate.year-1, month=12, day=1, hour=0, minute=0, second=0, microsecond=0)
        lastDay = fromDate.replace(year=firstDay.year, month=12, day=31,
                                   hour=23, minute=59, second=59, microsecond=999999)
        return (firstDay, lastDay)
    else:
        firstDayThisMonth = fromDate.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        lastDay = firstDayThisMonth - timedelta(days=1)
        lastDay = lastDay.replace(hour=23, minute=59, second=59, microsecond=999999)
        firstDay = firstDayThisMonth.replace(month=firstDayThisMonth.month-1)
        return (firstDay, lastDay)


def getPreviousWeek(fromDate=datetime.now()):
    """
    Returns a tuple of (startDate, endDate) for the min and max datetimes of the
    week previous to fromDate.  Assumes weeks start on Monday
    """
    start_delta = timedelta(days=fromDate.weekday(), weeks=1)
    firstDay = fromDate - start_delta
    lastDay = firstDay + timedelta(days=6)
    firstDay = firstDay.replace(hour=0, minute=0, second=0, microsecond=0)
    lastDay = lastDay.replace(hour=23, minute=59, second=59, microsecond=999999)

    return (firstDay, lastDay)


def getPreviousPeriod(fromDate, numDays):
    """
    Returns a tuple of (startDate, endDate) for the min and max datetimes of the
    period of length numDays ending the day before fromDate
    """
    start_delta = timedelta(days=numDays)
    lastDay = fromDate - timedelta(days=1)
    firstDay = lastDay - start_delta
    return (firstDay, lastDay)


def format_time_period_string(from_date, to_date=None):
    '''
    Formats the passed from_date and to_date into a string indicating time period:
    "from_date to to_date".  If to_date is None returns the same output as periodFormatter
    '''
    if from_date is None:
        return ''
    elif to_date is not None and from_date.date() == to_date.date():
        # This prevents periods like "12/8/16 to 12/8/16"
        to_date = None

    period_str = periodFormatter(from_date)

    if to_date is not None:
        period_str += ' to ' + periodFormatter(to_date)

    return period_str


def periodFormatter(date, period="day"):
    """
    Takes a datetime and a period and formats, returning a date formatted for insight display.
    Returns None if the period is not recognized.
    """
    if period == 'year':
        fmt = '%Y'
    elif period == 'quarter':
        fmt = '%x'
    elif period == 'month':
        fmt = '%B'
    elif period == 'week':
        fmt = '%x'
    elif period == 'day':
        fmt = '%x'
    elif period == 'hour':
        fmt = '%c'
    else:
        return None

    return date.strftime(fmt)


def integerTableFormat(val):
    """
    Returns a numeric formatted without decimal places and with comma-separated groups
    TODO: add localization
    """
    return '{:,.0f}'.format(val)


def dollarTableFormat(val):
    """
    Returns a numeric formatted with a preceding dollar sign, two decimal places
    and with comma-separated groups
    TODO: add localization
    """
    return '${:,.2f}'.format(val)


def decimalNumberFormat(val, num_places=1):
    """
    Returns a numeric formatted with two decimal places and with comma-separated groups
    TODO: add localization
    """
    retStr = '{:,.%(num_places)sf}' % {'num_places': num_places}
    return retStr.format(val)


def percentTableFormat(val):
    """
    Returns a numeric formatted with two decimal places and with a percent sign
    TODO: add localization
    """
    return '{:.2%}'.format(val)


def fancyDateTimeDeltaFormat(dt, from_date=datetime.now(), levels=2):
    """
    Format the date / time difference between the supplied date and
    the current time using approximate measurement boundaries
    TODO: make levels > 2 operational
    """
    delta = from_date - dt
    year = delta.days / 365
    month = delta.days / 30 - (12 * year)
    if year > 0:
        day = 0
    else:
        day = delta.days % 30
    hour = delta.seconds / 3600
    minute = delta.seconds / 60 - (60 * hour)

    vals = OrderedDict([('year', year),
                        ('month', month),
                        ('day', day),
                        ('hour', hour),
                        ('minute', minute)])

    fmt = []
    count_levels = 0
    for (period, value) in vals.items():
        if value:
            if value > 1:
                period += "s"
            fmt.append("%s %s" % (value, period))
            count_levels += 1
        if (count_levels >= levels):
            break
    return (", ".join(fmt))


def mode(df, key_cols, value_col, count_col):
    """
    Pandas does not provide a 'mode' aggregation function
    for its `GroupBy` objects. This function is meant to fill
    that gap, though the semantics are not exactly the same.

    The input is a DataFrame with the columns 'key_cols'
    that you would like to group on, and the column
    'value_col' for which you would like to obtain the mode.

    The output is a DataFrame with a record per group that has at least one mode
    (null values are not counted). The 'key_cols' are included as columns, 'value_col'
    contains a mode (ties are broken arbitrarily and deterministically) for each
    group, and 'count_col' indicates how many times each mode appeared in its group.

    taken from:
    http://stackoverflow.com/questions/15222754/group-by-pandas-dataframe-and-select-most-common-string-factor
    """
    return (df.groupby(key_cols + [value_col]).size()
            .to_frame(count_col).reset_index()
            .sort_values(count_col, ascending=False)
            .drop_duplicates(subset=key_cols))


def channels_from_common_transactions_df(df):
    """
    Takes a DataFrame with columns data_provider_name and data_provider_id
    and returns a list of corresponding Channels.
    """
    from r2d2.insights.models import Channel
    if df is None or df.shape[0] == 0:
        return []

    if 'data_provider_name' not in df or 'data_provider_id' not in df.columns:
        raise ValueError('DataFrame must have data_provider_name and data_provider_id columns')

    parseDF = df[['data_provider_name', 'data_provider_id']]
    parseDF = parseDF.drop_duplicates()

    channels = []
    for index, row in parseDF.iterrows():
        channels.append(Channel(data_provider_name=row['data_provider_name'],
                                data_provider_id=row['data_provider_id']))

    return channels

"""
OLD UNUSED INSIGHTS BELOW HERE.  Only used for testing
"""


class DataImportedInsight(BaseGenerator):
    """ Simple insight that generates - "Transactions data was imported" insight after the first data import
        and "Transactions data was updated" insight after each consecutive import, but not more than once every 12h """
    EMAIL_NOTIFICATION = False

    @classmethod
    def should_be_triggered(cls, account, success, fetched_from_all):
        if fetched_from_all:
            from r2d2.insights.models import Insight
            if not Insight.objects.filter(user=account.user, generator_class=cls.__name__,
                                          created__gte=datetime.now() - timedelta(hours=12)).exists():
                return True
        return False

    @classmethod
    def trigger(cls, account, success, fetched_from_all):
        from r2d2.insights.models import Insight
        insight = Insight(insight_model_id=0)

        if not Insight.objects.filter(user=account.user, generator_class=cls.__name__).exists():
            insight.text = "Transactions data was imported"
        else:
            insight.text = "Transactions data was updated"

        insight.is_initial = False
        return (insight, None, None)


class AverageProductsPerTransactions(BaseGenerator):
    """ Insights that generates -
    "Average number of products per transaction increased/decreased from X to Y compared to previous week" """

    map_f = Code("""
        function() {
            var products = 0;
            this.products.forEach(function(product) {
                products += product.quantity;
            });
            emit(1, {products_count: products, transactions_count: 1})
        }
    """)

    reduce_f = Code("""
        function reduce(key, values) {
            var result = {products_count: 0, transactions_count: 0};
            values.forEach(function(value) {
                result.products_count += value.products_count;
                result.transactions_count += value.transactions_count;
            });
            return result;
        }
    """)

    @classmethod
    def should_be_triggered(cls, account, success, fetched_from_all):
        return fetched_from_all

    @classmethod
    def trigger(cls, account, success, fetched_from_all):
        from r2d2.insights.models import Insight
        day_ago = datetime.now() - timedelta(days=1)
        eight_days_ago = day_ago - timedelta(days=7)
        last_24 = CommonTransaction.objects.filter(user_id=account.user_id, date__gt=day_ago)
        prev_week = CommonTransaction.objects.filter(user_id=account.user_id, date__gt=eight_days_ago).\
            filter(date__lt=day_ago)

        last_24 = list(last_24.map_reduce(cls.map_f, cls.reduce_f, "inline"))
        prev_week = list(prev_week.map_reduce(cls.map_f, cls.reduce_f, "inline"))
        last_24 = last_24[0].value['products_count'] / last_24[0].value['transactions_count'] if last_24 else 0
        prev_week = prev_week[0].value['products_count'] / prev_week[0].value['transactions_count'] if prev_week else 0

        insight = Insight(insight_model_id=2)
        if last_24 != prev_week:
            args = ("increased" if last_24 > prev_week else "decreased", prev_week, last_24)
            insight.text = "Average number of products per transaction in last 24h %s from %0.2f to %0.2f compared to\
 previous week" % args
            insight.is_initial = False
            return (insight, None, None)
        return None


class AverageTransactionsPerWeek(BaseGenerator):
    """ Insights that generates - "Number of transactions in last 24h increased/decreased from X to Y
        compared to previous week" """

    @classmethod
    def should_be_triggered(cls, account, success, fetched_from_all):
        return fetched_from_all

    @classmethod
    def trigger(cls, account, success, fetched_from_all):
        from r2d2.insights.models import Insight
        day_ago = datetime.now() - timedelta(days=1)
        eight_days_ago = day_ago - timedelta(days=7)

        last_24 = CommonTransaction.objects.filter(user_id=account.user_id, date__gt=day_ago).count()
        prev_week = CommonTransaction.objects.filter(user_id=account.user_id, date__gt=eight_days_ago).\
            filter(date__lt=day_ago).count() / 7.0

        insight = Insight(insight_model_id=1)
        if last_24 != prev_week:
            args = ("increased" if last_24 > prev_week else "decreased", prev_week, last_24)
            insight.text = "Number of transactions in last 24h %s from %0.2f to %d compared to previous week" % args
            insight.is_initial = False
            return (insight, None, None)
        return None

"""
Register all production InsightModels here
"""
InsightDispatcher.register(TopChannelInsight, 1)
InsightDispatcher.register(PeriodProductComparisonInsight, 2)
InsightDispatcher.register(TopPeriodInsight, 3)
InsightDispatcher.register(SalesByChannelInsight, 4)
InsightDispatcher.register(TopProductsInsight, 5)
InsightDispatcher.register(BestSellingProductsInsight, 6)
InsightDispatcher.register(ProductCountInsight, 7)
InsightDispatcher.register(DailyProductSalesInsight, 8)
InsightDispatcher.register(DiscountPercentageInsight, 9)
InsightDispatcher.register(DailyAverageProductsPerTransaction, 10)
InsightDispatcher.register(OldestTransactionInsight, 11)
InsightDispatcher.register(WeeklyAverageProductsPerTransaction, 12)
InsightDispatcher.register(AverageTransactionsPerPeriodInsight, 13)
InsightDispatcher.register(BestRevenueWeekEverInsight, 14)
InsightDispatcher.register(BestUnitsWeekEverInsight, 15)
InsightDispatcher.register(BestTransactionsWeekEverInsight, 16)
InsightDispatcher.register(ProductMultiplesInsight, 17)
InsightDispatcher.register(DaysSinceLastTransactionInsight, 18)
