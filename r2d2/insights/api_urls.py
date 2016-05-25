# -*- coding: utf-8 -*-
""" insights API urls """
from django.conf.urls import patterns
from django.conf.urls import url

from r2d2.insights.api import InsightsListAPI


urlpatterns = patterns(
    '',
    url(r'^$', InsightsListAPI.as_view(), name='insights'),
)
