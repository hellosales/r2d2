# -*- coding: utf-8 -*-
""" common layer """
from django_mongoengine import document
from django_mongoengine import fields

from r2d2.common_layer.signals import object_imported
from r2d2.common_layer.utils import map_id


class CommonTransactionProduct(document.EmbeddedDocument):
    """ unified product - to be embedded only """
    name = fields.StringField()
    sku = fields.StringField()
    quantity = fields.DecimalField(precision=10)
    price = fields.DecimalField(precision=2, required=True)
    tax = fields.DecimalField(precision=2, null=True, blank=True)
    discount = fields.DecimalField(precision=2, null=True, blank=True)
    total = fields.DecimalField(precision=2)


class CommonTransaction(document.Document):
    """ unified transaction """
    transaction_id = fields.StringField(db_index=True, unique=True)
    date = fields.DateTimeField()
    products = fields.ListField(fields.EmbeddedDocumentField('CommonTransactionProduct'))
    total_price = fields.DecimalField(precision=2)
    total_tax = fields.DecimalField(precision=2)
    total_discount = fields.DecimalField(precision=2)
    total_total = fields.DecimalField(precision=2)
    source = fields.StringField()


def object_imported_handler(**kwargs):
    importer_class = kwargs['importer_class']
    mapped_data = kwargs['mapped_data']
    transaction_id = map_id(importer_class, mapped_data.pop('transaction_id'))
    CommonTransaction.objects.filter(transaction_id=transaction_id).delete()
    CommonTransaction.objects.create(transaction_id=transaction_id, source=importer_class.__name__, **mapped_data)

object_imported.connect(object_imported_handler)
