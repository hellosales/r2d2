# -*- coding: utf-8 -*-
""" squareup admin """
from django.contrib import admin
from django_mongoengine.admin_support.decorators import dynamic_fields_list_display

from r2d2.data_importer.admin import DataImporterAdmin
from r2d2.squareup_api.models import ImportedSquareupPayment
from r2d2.squareup_api.models import SquareupAccount
from r2d2.squareup_api.models import SquareupErrorLog
from r2d2.utils.documents import StorageDocumentAdmin


class SquareupErrorAdmin(admin.TabularInline):
    model = SquareupErrorLog
    extra = 0
    readonly_fields = ('created_at', 'error', 'error_description')
    ordering = ('-created_at', )

    def has_add_permission(self, request):
        return False


class SquareupAccountAdmin(DataImporterAdmin):
    inlines = [SquareupErrorAdmin]

    def get_readonly_fields(self, request, obj=None):
        readonly_fields = super(SquareupAccountAdmin, self).get_readonly_fields(request, obj)
        return readonly_fields + ('merchant_id', 'token_expiration')


@dynamic_fields_list_display('squareup_id', 'created_at')
class ImportedSquareupPaymentAdmin(StorageDocumentAdmin):
    pass


admin.site.register(SquareupAccount, SquareupAccountAdmin)
admin.site.register(ImportedSquareupPayment, ImportedSquareupPaymentAdmin)
