# -*- coding: utf-8 -*-
""" squareup API urls """
from django.conf.urls import patterns
from django.conf.urls import url

from r2d2.squareup_api.api import SquareupAccountAPI
from r2d2.squareup_api.api import SquareupAccountListAPI
from r2d2.squareup_api.views import SquareupCallbackAPI


urlpatterns = patterns(
    '',
    url(r'^accounts$', SquareupAccountListAPI.as_view(), name='squareup-accounts'),
    url(r'^accounts/(?P<pk>[\d]+)$', SquareupAccountAPI.as_view(), name='squareup-accounts'),
    url(r'^auth/callback$', SquareupCallbackAPI.as_view(), name='squareup-callback'),
)
