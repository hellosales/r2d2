# -*- coding: utf-8 -*-
""" squareup API urls """
from django.conf.urls import patterns
from django.conf.urls import url

from r2d2.squareup_api.api import SquareupAccountAPI


urlpatterns = patterns(
    '',
    url(r'^store$', SquareupAccountAPI.as_view(), name='squareup-account'),
)
