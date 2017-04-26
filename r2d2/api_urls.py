# -*- coding: utf-8 -*-
from django.conf.urls import include
from django.conf.urls import patterns
from django.conf.urls import url

from rest_framework.routers import DefaultRouter


urlpatterns = patterns(
    '',
    url(r'^accounts/', include('r2d2.accounts.api_urls')),
    url(r'^', include('r2d2.insights.api_urls')),
    url(r'^notifications', include('r2d2.notifications.api_urls')),

    url(r'^data_importer/', include('r2d2.data_importer.api_urls')),
    url(r'^etsy/', include('r2d2.etsy_api.api_urls')),
    url(r'^shopify/', include('r2d2.shopify_api.api_urls')),
    url(r'^squareup/', include('r2d2.squareup_api.api_urls')),
    url(r'^stripe/', include('r2d2.stripe_api.api_urls')),
    url(r'^utils/', include('r2d2.utils.api_urls')),
)

router = DefaultRouter()
urlpatterns += router.urls
