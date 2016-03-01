# -*- coding: utf-8 -*-
from django.conf.urls import patterns, url

from rest_framework.routers import DefaultRouter

from r2d2.notifications.api import(
    NotificationsListApi, NotificationsApi,
)

urlpatterns = patterns(
    '',
    url(r'^$', NotificationsListApi.as_view(), name='notifications_api'),
    url(r'^/(?P<pk>[\d]+)$', NotificationsApi.as_view(), name='notifications_api'),

)

router = DefaultRouter()
urlpatterns += router.urls
