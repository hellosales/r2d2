# -*- coding: utf-8 -*-
""" utils API urls """
from django.conf.urls import patterns
from django.conf.urls import url

from r2d2.utils.api import DjMoneyUpdateRatesAPI
from r2d2.utils.api import DjangoClearSessionsAPI


urlpatterns = patterns(
    '',
    url(r'^update-rates$', DjMoneyUpdateRatesAPI.as_view(), name='djmoney-update-rates-api'),
    url(r'^clearsessions$', DjangoClearSessionsAPI.as_view(), name='django-clearsessions-api'),
)
