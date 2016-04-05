# -*- coding: utf-8 -*-
""" squareup admin """
from django.contrib import admin
from django_mongoengine.admin_support.decorators import dynamic_fields_list_display

from r2d2.squareup_api.models import SquareupAccount
from r2d2.squareup_api.models import ImportedSquareupPayment
from r2d2.utils.documents import StorageDocumentAdmin


class SquareupAccountAdmin(admin.ModelAdmin):
    """ squareup model admin """
    list_display = ('name', 'user', 'is_authorized')


@dynamic_fields_list_display('squareup_id', 'created_at')
class ImportedSquareupPaymentAdmin(StorageDocumentAdmin):
    pass


admin.site.register(SquareupAccount, SquareupAccountAdmin)
admin.site.register(ImportedSquareupPayment, ImportedSquareupPaymentAdmin)
