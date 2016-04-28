# -*- coding: utf-8 -*-
""" common layer """
from django_mongoengine import document
from django_mongoengine import fields

from r2d2.common_layer.signals import object_imported
from r2d2.common_layer.utils import map_id


class CommonTransactionProduct(document.EmbeddedDocument):
    """ unified product - to be embedded only """
    name = fields.StringField(required=True)
    sku = fields.StringField(required=True)
    quantity = fields.IntField(required=True)
    price = fields.DecimalField(precision=2, required=True)
    tax = fields.DecimalField(precision=2, required=False)
    discount = fields.DecimalField(precision=2, required=False)
    total = fields.DecimalField(precision=2, required=True)


class CommonTransaction(document.Document):
    """ unified transaction """
    transaction_id = fields.StringField(required=True, db_index=True, unique=True)
    date = fields.DateTimeField(required=True)
    products = fields.ListField(fields.EmbeddedDocumentField('CommonTransactionProduct'))
    total_price = fields.DecimalField(precision=2, required=True)
    total_tax = fields.DecimalField(precision=2, required=False)
    total_discount = fields.DecimalField(precision=2, required=False)
    total_total = fields.DecimalField(precision=2, required=True)
    source = fields.StringField(required=True)


def object_imported_handler(**kwargs):
    importer_class = kwargs['importer_class']
    mapped_data = kwargs['mapped_data']
    transaction_id = map_id(importer_class, mapped_data.pop('transaction_id'))
    CommonTransaction.objects.filter(transaction_id=transaction_id).delete()
    CommonTransaction.objects.create(transaction_id=transaction_id, source=importer_class.__name__, **mapped_data)

object_imported.connect(object_imported_handler)
