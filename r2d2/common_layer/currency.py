# -*- coding: utf-8 -*-
'''
Module for currency handling and conversion
'''
from datetime import date
import pandas as pd

from r2d2.common_layer.models import ExchangeRate, ExchangeRateSource
import r2d2.common_layer.models as clmodels
import r2d2.common_layer.utils as clutils


class MoneyConverter(object):
    """
    Class that tracks historic exchange rates and can convert between any two
    tracked rates for a requested date.
    """
    __exchange_rates = None

    @classmethod
    def load_exchange_rates(cls, force=False):
        if cls.__exchange_rates is not None and force == False:
            return
        
        cls.__exchange_rates = cls.exchange_rates_to_df(ExchangeRate.objects.filter())
        
        
    @classmethod
    def get_rate_cached(cls, from_curr, to_curr, date, force_date=True):
        """
        Returns an exchange rate for the two currencies for the date.
        
        from_curr:  the currency to convert from
        to_curr:  the currency to convert to
        date:  the date to provide a rate for
        force_date:  if true will throw an exception when a rate can't be found 
            for a given date.  If False will return the rate for the date nearest
            the date requested.
        TODO: TEST
        """
        cls.load_exchange_rates()
        
        if force_date:
            rates = MoneyConverter.__exchange_rates[(MoneyConverter.__exchange_rates.currency==from_curr)
                                                    & (MoneyConverter.__exchange_rates.base_currency==to_curr)
                                                    & (MoneyConverter.__exchange_rates.date==date)]
        else:
            rates = MoneyConverter.__exchange_rates[(MoneyConverter.__exchange_rates.currency==from_curr)
                                                    & (MoneyConverter.__exchange_rates.base_currency==to_curr)
                                                    & (MoneyConverter.__exchange_rates.date==clutils.nearest(date, MoneyConverter.__exchange_rates.date.unique()))]
            
        
        if rates.shape[0] > 1:
            rate = rates[0]
            raise RuntimeWarning('More than one exchange rate/date combination found for %(from_curr)s and %(date)s'%{'from_curr':from_curr, 'date':date})
        elif rates.shape[0] == 0:
            raise LookupError('No ExchangeRate could be found for these currencies and dates')
        
        return(rate.iloc[0].value)

def exchange_rates_to_df(rates):
    """
    Turns QuerySet of DJMoneyRatesRate from the DB into a DataFrame
    Returns None if passed DJMoneyRatesRate is empty
    """
    if rates is None or len(rates) == 0:
        return None
    
    id = []
    currency  = []
    value  = []
    base_currency  = []
    date  = []

    columns = ['id',
               'currency',
               'value',
               'base_currency',
               'date']

    for rate in rates:
        id.append(rate.id),
        currency.append(rate.currency)
        value.append(rate.value)
        base_currency.append(rate.source.base_currency)
        date.append(rate.date)
        
    zipped = zip( id,
                  currency,
                  value,
                  base_currency,
                  date)
    
    return(pd.DataFrame(zipped,columns=['id','currency','value','base_currency','date']))
    

def get_rate(from_curr, to_curr, date, force_date=True):
    """
    Returns an exchange rate for the two currencies for the date.
    
    from_curr:  the currency to convert from
    to_curr:  the currency to convert to
    date:  the date to provide a rate for
    force_date:  if true will throw an exception when a rate can't be found 
        for a given date.  If False will return the rate for the date nearest
        the date requested.
    TODO: TEST
    """
    rates = ExchangeRate.objects.filter(currency=from_curr, date=date, source__base_currency=to_curr)
    
    if len(rates) > 1:
        rate = rates[0]
        raise RuntimeWarning('More than one exchange rate/date combination found for %(from_curr)s and %(date)s'%{'from_curr':from_curr, 'date':date})
    elif len(rates)==0:
        if force_date:
            raise LookupError('No ExchangeRate could be found for these currencies and dates')
        else:
            # Get the rate for the closest available date
            rates = ExchangeRate.objects.filter(currency=from_curr, source__base_currency=to_curr)
            rates_dates = {}
            for rate in rates:
                rates_dates[rate.date] = rate
                
            rate = rates_dates[clutils.nearest(date,rates_dates.keys())]
    else:
        rate = rates[0]
    
    return(rate)


def convert(amount, from_curr, to_curr, date, force_date=True, use_cache=False):
    """
    Converts the passed amount from from_curr to to_curr, using the exchange
    rate on the given date.
    
    amount:  the monetary amount to convert, expressed in the currency from_curr
    from_curr:  the currency to convert from
    to_curr:  the currency to convert to
    date:  the date to find an exchange rate for
    force_date:  if true will throw an exception when a rate can't be found 
        for a given date.  If False will return the rate for the date nearest
        the date requested.
    TODO: TEST
    """
    if use_cache:
        return (MoneyConverter.get_rate_cached(from_curr, to_curr, date, force_date) * amount)
    else:
        return (get_rate(from_curr, to_curr, date, force_date) * amount)

    
def convert_common_transactions_df(df, to_curr, force_date=True):
    """
    Converts all monetary values in a DataFrame of CommonTransactions (as returned
    by r2d2.common_layer.models.common_transactions_to_df() from the currency specified
    in the currency_code column and the date specified in the date column, to 
    the currency to_curr.
    
    This method tested to be 100x faster than using convert()
    
    df:  the dataframe of CommonTransactions (as returned by r2d2.common_layer.models.common_transactions_to_df())
    to_curr:  the currency to convert to
    force_date:  if True will look for an exact currency conversion for the date
        specified in the DataFrame.  If False will return the rate for the date nearest
        the date requested.  Defaults to True
    """
    if df is None or df.shape[0] == 0:
        return None
    
    rates = ExchangeRate.objects.filter(source__base_currency=to_curr, currency__in=df.currency_code.unique().tolist())
    if rates is None or len(rates)==0:
        return None
    rdf = exchange_rates_to_df(rates)
    
    if force_date:
        df['nearest_date']=df.date.dt.date
    else:
        df['nearest_date']=df.date.dt.date.apply(clutils.nearest,args=([rdf.date.tolist()]))

    df = df.merge(rdf, 
                  how='left', 
                  left_on=['currency_code','nearest_date'], 
                  right_on=['currency','date'],
                  suffixes=('','_rate'))
    
    converted = '_converted'
    for column in clmodels.get_money_columns():
        df[column+converted] = df[column] * df.value

    return(df)

