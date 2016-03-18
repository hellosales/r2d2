# -*- coding: utf-8 -*-
""" squareup API urls """
from django.conf.urls import patterns
from django.conf.urls import url

from r2d2.squareup_api.api import SquareupAccountAPI
from r2d2.squareup_api.api import SquareupAccountListAPI


urlpatterns = patterns(
    '',
    url(r'^store$', SquareupAccountListAPI.as_view(), name='squareup-account'),
    url(r'^store/(?P<pk>[\d]+)$', SquareupAccountAPI.as_view(), name='squareup-account'),
)
