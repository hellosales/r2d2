# -*- coding: utf-8 -*-
""" (c) @ Arabel.la 2016

    shopify API urls

    authors: Pawel Krzyzaniak"""
from django.conf.urls import patterns
from django.conf.urls import url

from r2d2.shopify_api.api import ShopifyStoreAPI


urlpatterns = patterns('',
    url(r'^store$', ShopifyStoreAPI.as_view(), name='shopify-store'),
)
