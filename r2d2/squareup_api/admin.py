# -*- coding: utf-8 -*-
""" squareup admin """
from django.contrib import admin
from django_mongoengine.admin_support.decorators import dynamic_fields_list_display

from r2d2.data_importer.admin import DataImporterAdmin
from r2d2.squareup_api.models import ImportedSquareupPayment
from r2d2.squareup_api.models import SquareupAccount
from r2d2.utils.documents import StorageDocumentAdmin


class SquareupAccountAdmin(DataImporterAdmin):
    def get_readonly_fields(self, request, obj=None):
        readonly_fields = super(SquareupAccountAdmin, self).get_readonly_fields(request, obj)
        return readonly_fields + ('in_authorization', 'merchant_id', 'token_expiration')


@dynamic_fields_list_display('squareup_id', 'created_at')
class ImportedSquareupPaymentAdmin(StorageDocumentAdmin):
    pass


admin.site.register(SquareupAccount, SquareupAccountAdmin)
admin.site.register(ImportedSquareupPayment, ImportedSquareupPaymentAdmin)
