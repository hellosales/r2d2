# -*- coding: utf-8 -*-
""" etsy API urls """
from django.conf.urls import patterns
from django.conf.urls import url

from r2d2.etsy_api.api import EtsyAccountAPI
from r2d2.etsy_api.api import EtsyAccountListAPI


urlpatterns = patterns(
    '',
    url(r'^accounts$', EtsyAccountListAPI.as_view(), name='etsy-accounts'),
    url(r'^accounts/(?P<pk>[\d]+)$', EtsyAccountAPI.as_view(), name='etsy-accounts'),
)
