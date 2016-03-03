# -*- coding: utf-8 -*-
""" (c) @ Arabel.la 2016

    shopify admin

    authors: Pawel Krzyzaniak"""
from django.contrib import admin

from r2d2.shopify_api.models import ShopifyStore


class ShopifyStoreAdmin(admin.ModelAdmin):
    list_display = ('name', 'user', 'is_authorized')


admin.site.register(ShopifyStore, ShopifyStoreAdmin)
