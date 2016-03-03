# -*- coding: utf-8 -*-
""" (c) @ Arabel.la 2016

    shopify urls

    authors: Pawel Krzyzaniak"""
from django.conf.urls import patterns
from django.conf.urls import url

from r2d2.shopify_api.views import ShopifyCallbackAPI


urlpatterns = patterns('',
    url(r'^auth/callback$', ShopifyCallbackAPI.as_view(), name='shopify-callback'),
)
