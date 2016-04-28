# -*- coding: utf-8 -*-
""" insights generators
    each generator must be connected with fetched_data signal in order to work """
from datetime import datetime
from datetime import timedelta


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

    @classmethod
    def should_be_triggered(cls, account, success, fetched_from_all):
        return fetched_from_all

    @classmethod
    def trigger(cls, account, success, fetched_from_all):
        pass  #


class AverageTransactionsPerWeek(BaseGenerator):
    """ Insights that generates - "Average number of transactions increased/decreased from X to Y
        compared to previous week" """

    @classmethod
    def should_be_triggered(cls, account, success, fetched_from_all):
        return fetched_from_all

    @classmethod
    def trigger(cls, account, success, fetched_from_all):
        pass  #
