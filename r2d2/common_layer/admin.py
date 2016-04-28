# -*- coding: utf-8 -*-
from django.contrib import admin

from django_mongoengine import mongo_admin

from r2d2.common_layer.models import CommonTransaction


class CommonTransactionAdmin(mongo_admin.JSONDocumentAdmin):
    list_display = ('transaction_id', 'date', 'products', 'total_price', 'total_tax', 'total_discount', 'total_total')


admin.site.register(CommonTransaction, CommonTransactionAdmin)
