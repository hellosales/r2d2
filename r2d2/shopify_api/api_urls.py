# -*- coding: utf-8 -*-
""" shopify API urls """
from django.conf.urls import patterns
from django.conf.urls import url

from r2d2.shopify_api.api import ShopifyStoreAPI
from r2d2.shopify_api.api import ShopifyStoreListAPI


urlpatterns = patterns(
    '',
    url(r'^store$', ShopifyStoreListAPI.as_view(), name='shopify-store'),
    url(r'^store/(?P<pk>[\d]+)$', ShopifyStoreAPI.as_view(), name='shopify-store'),
)
