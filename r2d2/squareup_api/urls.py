# -*- coding: utf-8 -*-
""" squareup urls """
from django.conf.urls import patterns
from django.conf.urls import url

from r2d2.squareup_api.views import SquareupCallbackAPI


urlpatterns = patterns(
    '',
    url(r'^auth/callback$', SquareupCallbackAPI.as_view(), name='squareup-callback'),
)
