# -*- coding: utf-8 -*-
""" etsy callback url """
from django.conf.urls import patterns
from django.conf.urls import url

from r2d2.etsy_api.views import EtsyCallbackAPI


urlpatterns = patterns('',
    url(r'^auth/callback$', EtsyCallbackAPI.as_view(), name='etsy-callback'),
)
