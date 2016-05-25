# -*- coding: utf-8 -*-
""" insights generators
    each generator must be connected with fetched_data signal in order to work """
from bson.code import Code
from datetime import datetime
from datetime import timedelta

from r2d2.common_layer.models import CommonTransaction


class BaseGenerator(object):
    """ Base generator class """

    @classmethod
    def should_be_triggered(cls, account, success, fetched_from_all):
        raise NotImplementedError

    @classmethod
    def trigger(cls, account, success, fetched_from_all):
        raise NotImplementedError

    @classmethod
    def handle_data_fetched(cls, **kwargs):
        from r2d2.insights.models import Insight

        account = kwargs['account']
        success = kwargs['success']
        fetched_from_all = kwargs['fetched_from_all']
        if cls.should_be_triggered(account, success, fetched_from_all):
            insight_text = cls.trigger(account, success, fetched_from_all)
            if insight_text:
                Insight.objects.create(user=account.user, text=insight_text, generator_class=cls.__name__)


class DataImportedInsight(BaseGenerator):
    """ Simple insight that generates - "Transactions data was imported" insight after the first data import
        and "Transactions data was updated" insight after each consecutive import, but not more than once every 12h """

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

        if not Insight.objects.filter(user=account.user, generator_class=cls.__name__).exists():
            return "Transactions data was imported"
        return "Transactions data was updated"


class AverageProductsPerTransactions(BaseGenerator):
    """ Insights that generates - "Average number of products per transaction increased/decreased from X to Y
        compared to previous week" """

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
        day_ago = datetime.now() - timedelta(days=1)
        eight_days_ago = day_ago - timedelta(days=7)
        last_24 = CommonTransaction.objects.filter(user_id=account.user_id, date__gt=day_ago)
        prev_week = CommonTransaction.objects.filter(user_id=account.user_id, date__gt=eight_days_ago).\
            filter(date__lt=day_ago)

        last_24 = list(last_24.map_reduce(cls.map_f, cls.reduce_f, "inline"))
        prev_week = list(prev_week.map_reduce(cls.map_f, cls.reduce_f, "inline"))
        last_24 = last_24[0].value['products_count'] / last_24[0].value['transactions_count'] if last_24 else 0
        prev_week = prev_week[0].value['products_count'] / prev_week[0].value['transactions_count'] if prev_week else 0

        if last_24 != prev_week:
            args = ("increased" if last_24 > prev_week else "decreased", prev_week, last_24)
            return ("Average number of products per transaction in last 24h"
                    " %s from %0.2f to %0.2f compared to previous week" % args)
        return None


class AverageTransactionsPerWeek(BaseGenerator):
    """ Insights that generates - "Number of transactions in last 24h increased/decreased from X to Y
        compared to previous week" """

    @classmethod
    def should_be_triggered(cls, account, success, fetched_from_all):
        return fetched_from_all

    @classmethod
    def trigger(cls, account, success, fetched_from_all):
        day_ago = datetime.now() - timedelta(days=1)
        eight_days_ago = day_ago - timedelta(days=7)

        last_24 = CommonTransaction.objects.filter(user_id=account.user_id, date__gt=day_ago).count()
        prev_week = CommonTransaction.objects.filter(user_id=account.user_id, date__gt=eight_days_ago).\
            filter(date__lt=day_ago).count() / 7.0

        if last_24 != prev_week:
            args = ("increased" if last_24 > prev_week else "decreased", prev_week, last_24)
            return "Number of transactions in last 24h %s from %0.2f to %d compared to previous week" % args
        return None
