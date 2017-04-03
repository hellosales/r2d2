# -*- coding: utf-8 -*-
""" stripe API urls """
from django.conf.urls import patterns
from django.conf.urls import url

from r2d2.stripe_api.api import StripeAccountAPI
from r2d2.stripe_api.api import StripeAccountListAPI


urlpatterns = patterns(
    '',
    url(r'^accounts$', StripeAccountListAPI.as_view(), name='stripe-accounts'),
    url(r'^accounts/(?P<pk>[\d]+)$', StripeAccountAPI.as_view(), name='stripe-accounts'),
)
