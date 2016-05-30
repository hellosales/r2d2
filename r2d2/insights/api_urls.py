# -*- coding: utf-8 -*-
""" insights API urls """
from django.conf.urls import patterns
from django.conf.urls import url

from r2d2.insights.api import HeaderDataApi
from r2d2.insights.api import InsightsListAPI


urlpatterns = patterns(
    '',
    url(r'^insights$', InsightsListAPI.as_view(), name='insights'),
    url(r'^header-data$', HeaderDataApi.as_view(), name='header_data_api'),
)
