# -*- coding: utf-8 -*-
""" shopify admin """
from django.contrib import admin

from r2d2.shopify_api.models import ShopifyStore


class ShopifyStoreAdmin(admin.ModelAdmin):
    list_display = ('name', 'user', 'is_authorized')


admin.site.register(ShopifyStore, ShopifyStoreAdmin)
