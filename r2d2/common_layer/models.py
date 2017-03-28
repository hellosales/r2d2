# -*- coding: utf-8 -*-
""" common layer """
from django_mongoengine import document, fields
from decimal import Decimal
from django.db import models

import pandas as pd
from collections import OrderedDict

from r2d2.common_layer.signals import object_imported
from r2d2.common_layer.utils import map_id


class CommonTransactionProduct(document.EmbeddedDocument):
    """
    unified product - to be embedded only
    Note: precision for DecimalField is set to 5.  This is one more digit than the
    maximum currency exponent as indicated in https://en.wikipedia.org/wiki/ISO_4217
    """
    name = fields.StringField()
    sku = fields.StringField()
    quantity = fields.DecimalField(precision=10)
    price = fields.DecimalField(precision=5, required=True)
    tax = fields.DecimalField(precision=5, null=True, blank=True)
    discount = fields.DecimalField(precision=5, null=True, blank=True)
    total = fields.DecimalField(precision=5)


class CommonTransaction(document.Document):
    """
    unified transaction.
    Note: precision for DecimalField is set to 5.  This is one more digit than the
    maximum currency exponent as indicated in https://en.wikipedia.org/wiki/ISO_4217
    """
    user_id = fields.IntField(db_index=True)
    transaction_id = fields.StringField(db_index=True, unique=True)
    date = fields.DateTimeField(db_index=True)
    products = fields.ListField(fields.EmbeddedDocumentField('CommonTransactionProduct'))
    total_price = fields.DecimalField(precision=5)
    total_tax = fields.DecimalField(precision=5)
    total_discount = fields.DecimalField(precision=5)
    total_total = fields.DecimalField(precision=5)
    currency_code = fields.StringField()
    source = fields.StringField()

    # These two fields allow us to do a DB lookup for the AbstractDataProvider subclass.
    # TODO: modify this if this is managed more flexibly through the DB later
    data_provider_name = fields.StringField()
    data_provider_id = fields.IntField()


class CommonTransactionDataFrame():
    """
    A pandas.DataFrame of flattened CommonTransaction and CommonTransactionProduct data.
    Intended as a read-only copy of this data.  This class exists to encapsulate custom
    MongoDB calls to improve read performance.
    """
    # Should exactly mirror all CommonTransaction members aside from products
    _metas = ['_id',
              'user_id',
              'transaction_id',
              'date',
              'total_price',
              'total_tax',
              'total_discount',
              'total_total',
              'currency_code',
              'source',
              'data_provider_id',
              'data_provider_name']

    @classmethod
    def find(cls, user_id=None, data_provider_name=None, data_provider_id=None,
             source=None, start_date=None, end_date=None, transaction_id=None):
        """
        Access the MongoDB datastore and return a pandas.DataFrame of flattened
        CommonTransaction results with they're child products
        """
        # Get the collection this way to take advantage of mongoengine's underlying
        # connection management
        coll = CommonTransaction._get_collection()

        find_dict = OrderedDict()  # order matters for MongoDB indexes
        if user_id:
            find_dict['user_id'] = user_id
        if data_provider_name:
            find_dict['data_provider_name'] = data_provider_name
        if data_provider_id:
            find_dict['data_provider_id'] = data_provider_id
        if source:
            find_dict['source'] = source
        if start_date:
            find_dict['start_date'] = start_date
        if end_date:
            find_dict['end_date'] = end_date
        if transaction_id:
            find_dict['transaction_id'] = transaction_id

        results = list(coll.find(find_dict))

        txnsDF = pd.io.json.json_normalize(results, 'products', cls._metas, record_prefix='product_')

        # Apply our own data types to monetary columns and the user_id.  This
        # adds significant time (4x) to the function processing, but seems necessary
        # because we're side stepping mongoengine's handling of the float to Decimal
        # conversion.  Upgrading to MongoDB 3.4 might allow this code to be removed
        # because that version supports a decimal BSON type.
        # Note that we first convert float columns to strings, then to Decimal,
        # because going directly to Decimal from float was introducing binary rounding
        # errors.
        # TODO:  read comment and adjust/remove astype,apply calls as needed

        # no results
        if txnsDF.shape[0] == 0:
            return txnsDF

        for col in get_money_columns():
            txnsDF[col] = txnsDF[col].astype(str)
            txnsDF[col] = txnsDF[col].apply(Decimal)
        txnsDF.user_id = txnsDF.user_id.apply(int)

        return txnsDF


class ExchangeRateSource(models.Model):
    """
    Unmanaged model for the djmoney_rates_ratesource table that shows what the
    source rate is for all rates in the djmoney_rates_rate table
    """
    id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=100)
    last_update = models.DateField()
    base_currency = models.CharField(max_length=3)

    class Meta:
        managed = False
        db_table = 'djmoney_rates_ratesource'


class ExchangeRate(models.Model):
    """
    Unmanaged model for the djmoney_rates_rate table that tracks historical
    foreign currency exchange rates.
    """
    id = models.IntegerField(primary_key=True)
    currency = models.CharField(max_length=3)
    value = models.DecimalField(max_digits=20, decimal_places=6)
    source = models.ForeignKey(ExchangeRateSource, on_delete=models.DO_NOTHING)
    date = models.DateField()

    class Meta:
        managed = False
        db_table = 'djmoney_rates_rate'


def unpack(txn):
    """
    Returns a flattened CommonTransaction with its CommonTransactionProducts
    as a list of tuples (using zip())
    """

    user_ids = []
    transaction_ids = []
    dates = []
    total_prices = []
    total_taxs = []
    total_discounts = []
    total_totals = []
    currency_codes = []
    sources = []
    data_provider_name = []
    data_provider_id = []
    product_name = []
    product_sku = []
    product_quantity = []
    product_price = []
    product_tax = []
    product_discount = []
    product_total = []

    for product in txn.products:
        user_ids.append(txn.user_id)
        transaction_ids.append(txn.transaction_id)
        dates.append(txn.date)
        total_prices.append(txn.total_price)
        total_taxs.append(txn.total_tax)
        total_discounts.append(txn.total_discount)
        total_totals.append(txn.total_total)
        currency_codes.append(txn.currency_code)
        sources.append(txn.source)
        data_provider_name.append(txn.data_provider_name)
        data_provider_id.append(txn.data_provider_id)
        product_name.append(product.name)
        product_sku.append(product.sku)
        product_quantity.append(product.quantity)
        product_price.append(product.price)
        product_tax.append(product.tax)
        product_discount.append(product.discount)
        product_total.append(product.total)

    zipped = zip(user_ids,
                 transaction_ids,
                 dates,
                 total_prices,
                 total_taxs,
                 total_discounts,
                 total_totals,
                 currency_codes,
                 sources,
                 data_provider_name,
                 data_provider_id,
                 product_name,
                 product_sku,
                 product_quantity,
                 product_price,
                 product_tax,
                 product_discount,
                 product_total)

    return zipped


def get_unpack_columns():
    """
    Returns a tuple of column names that correspond to the tuples returned by unpack
    """
    return(('user_id',
            'transaction_id',
            'date',
            'total_price',
            'total_tax',
            'total_discount',
            'total_total',
            'currency_code',
            'source',
            'data_provider_name',
            'data_provider_id',
            'product_name',
            'product_sku',
            'product_quantity',
            'product_price',
            'product_tax',
            'product_discount',
            'product_total'))


def get_money_columns():
    """
    Returns a list of columns names that hold monetary fields
    TODO: can unify this and get_unpack_columns to draw from a single, static
        list of columns with some meaning.
    """
    return(['total_price',
            'total_tax',
            'total_discount',
            'total_total',
            'product_price',
            'product_tax',
            'product_discount',
            'product_total'])


def common_transactions_to_df(common_transactions):
    '''
    Turns a list of CommonTransaction objects into a DataFrame, flattening
    out the CommonTransactionProduct children in the process.  Returns None
    if the passed iterator is empty
    '''
    if len(common_transactions) == 0:
        return(None)

    txnList = []
    for txn in common_transactions:
        txnList.extend(unpack(txn))

    retDF = pd.DataFrame(txnList)
    retDF.columns = get_unpack_columns()
    retDF['date'] = pd.to_datetime(retDF['date'])  # allows for fast date searching/indexing

    return retDF


def object_imported_handler(**kwargs):
    importer_account = kwargs['importer_account']
    mapped_data = kwargs['mapped_data']
    transaction_id = map_id(importer_account, mapped_data.pop('transaction_id'))
    CommonTransaction.objects.filter(transaction_id=transaction_id).delete()
    CommonTransaction.objects.create(transaction_id=transaction_id,
                                     source=importer_account.official_channel_name,
                                     data_provider_name=importer_account.__class__.__name__,
                                     data_provider_id=importer_account.id,
                                     **mapped_data)

object_imported.connect(object_imported_handler)
