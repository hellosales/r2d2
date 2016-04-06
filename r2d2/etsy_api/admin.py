# -*- coding: utf-8 -*-
""" etsy models admin """
from django.contrib import admin
from django_mongoengine.admin_support.decorators import dynamic_fields_list_display

from r2d2.data_importer.admin import DataImporterAdmin
from r2d2.etsy_api.models import EtsyAccount
from r2d2.etsy_api.models import ImportedEtsyReceipt
from r2d2.etsy_api.models import ImportedEtsyShop
from r2d2.etsy_api.models import ImportedEtsyTransaction
# from r2d2.etsy_api.models import ImportedEtsyPayment
# from r2d2.etsy_api.models import ImportedEtsyPaymentAdjustment
from r2d2.utils.documents import StorageDocumentAdmin


class EtsyAccountAdmin(DataImporterAdmin):
    def get_readonly_fields(self, request, obj=None):
        readonly_fields = super(EtsyAccountAdmin, self).get_readonly_fields(request, obj)
        return readonly_fields + ('request_token',)


@dynamic_fields_list_display('shop_id', 'shop_name', 'user_id')
class ImportedEtsyShopAdmin(StorageDocumentAdmin):
    pass


@dynamic_fields_list_display('transaction_id', 'seller_user_id', 'title', 'price', 'receipt_id')
class ImportedEtsyTransactionAdmin(StorageDocumentAdmin):
    pass


@dynamic_fields_list_display('receipt_id', 'last_modified_tsz')
class ImportedEtsyReceiptAdmin(StorageDocumentAdmin):
    pass


# @dynamic_fields_list_display('payment_id', 'receipt_id')
# class ImportedEtsyPaymentAdmin(StorageDocumentAdmin):
#     pass


# @dynamic_fields_list_display('payment_adjustment_id', 'payment_id', 'status')
# class ImportedEtsyPaymentAdjustmentAdmin(StorageDocumentAdmin):
#     pass


admin.site.register(EtsyAccount, EtsyAccountAdmin)
admin.site.register(ImportedEtsyShop, ImportedEtsyShopAdmin)
admin.site.register(ImportedEtsyTransaction, ImportedEtsyTransactionAdmin)
admin.site.register(ImportedEtsyReceipt, ImportedEtsyReceiptAdmin)
# admin.site.register(ImportedEtsyPayment, ImportedEtsyPaymentAdmin)
# admin.site.register(ImportedEtsyPaymentAdjustment, ImportedEtsyPaymentAdjustmentAdmin)
