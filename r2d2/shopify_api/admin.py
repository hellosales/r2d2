# -*- coding: utf-8 -*-
""" shopify admin """
from django.contrib import admin
from django_mongoengine.admin_support.decorators import dynamic_fields_list_display

from r2d2.data_importer.admin import DataImporterAdmin
from r2d2.shopify_api.models import ImportedShopifyOrder
from r2d2.shopify_api.models import ShopifyStore
from r2d2.utils.documents import StorageDocumentAdmin


class ShopifyStoreAdmin(DataImporterAdmin):
    def get_readonly_fields(self, request, obj=None):
        readonly_fields = super(ShopifyStoreAdmin, self).get_readonly_fields(request, obj)
        return readonly_fields + ('name',)


@dynamic_fields_list_display('shopify_id', 'total_price', 'email', 'created_at')
class ShopifyOrderAdmin(StorageDocumentAdmin):
    pass


admin.site.register(ShopifyStore, ShopifyStoreAdmin)
admin.site.register(ImportedShopifyOrder, ShopifyOrderAdmin)
