# -*- coding: utf-8 -*-
from django.conf.urls import patterns, url, include

from rest_framework.routers import DefaultRouter


urlpatterns = patterns(
    '',
    url(r'^accounts/', include('r2d2.accounts.api_urls')),
    url(r'^notifications', include('r2d2.notifications.api_urls')),
)

router = DefaultRouter()
urlpatterns += router.urls
