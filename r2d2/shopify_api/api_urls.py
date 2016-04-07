# -*- coding: utf-8 -*-
""" shopify API urls """
from django.conf.urls import patterns
from django.conf.urls import url

from r2d2.shopify_api.api import ShopifyStoreAPI
from r2d2.shopify_api.api import ShopifyStoreListAPI
from r2d2.shopify_api.views import ShopifyCallbackAPI


urlpatterns = patterns(
    '',
    url(r'^stores$', ShopifyStoreListAPI.as_view(), name='shopify-stores'),
    url(r'^stores/(?P<pk>[\d]+)$', ShopifyStoreAPI.as_view(), name='shopify-stores'),
    url(r'^auth/callback$', ShopifyCallbackAPI.as_view(), name='shopify-callback'),
)
