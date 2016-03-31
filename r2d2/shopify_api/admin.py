# -*- coding: utf-8 -*-
""" shopify admin """
from django.contrib import admin
from django_mongoengine import mongo_admin
from django_mongoengine.admin_support.decorators import dynamic_fields_list_display

from r2d2.shopify_api.models import ShopifyStore
from r2d2.shopify_api.models import ImportedShopifyOrder
from r2d2.utils.documents import StorageDocumentAdmin


class ShopifyStoreAdmin(admin.ModelAdmin):
    list_display = ('name', 'user', 'is_authorized')


@dynamic_fields_list_display('id', 'b', 'c')
class ShopifyOrderAdmin(StorageDocumentAdmin):
    pass


admin.site.register(ShopifyStore, ShopifyStoreAdmin)
admin.site.register(ImportedShopifyOrder, ShopifyOrderAdmin)
