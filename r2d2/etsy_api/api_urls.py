# -*- coding: utf-8 -*-
""" etsy API urls """
from django.conf.urls import patterns
from django.conf.urls import url

from r2d2.etsy_api.api import EtsyAccountAPI
from r2d2.etsy_api.api import EtsyAccountListAPI


urlpatterns = patterns(
    '',
    url(r'^account$', EtsyAccountListAPI.as_view(), name='etsy-account'),
    url(r'^account/(?P<pk>[\d]+)$', EtsyAccountAPI.as_view(), name='etsy-account'),
)
