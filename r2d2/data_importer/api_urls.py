# -*- coding: utf-8 -*-
""" data_importer API urls """
from django.conf.urls import patterns
from django.conf.urls import url

from r2d2.data_importer.api import DataImporterAccountsAPI,\
    DataImporterGenerateOauthUrl,\
    DataImporterMonitorRateLimits,\
    SuggestionCreateAPI,\
    DataImporterRunFetchingData


urlpatterns = patterns(
    '',
    url(r'^accounts$', DataImporterAccountsAPI.as_view(), name='data-importer-accounts'),
    url(r'^generate-oauth-url$', DataImporterGenerateOauthUrl.as_view(), name='data-importer-generate-oauth-url'),
    url(r'^source-sugesstions$', SuggestionCreateAPI.as_view(), name='source-suggestions-api'),
    url(r'^schedule-fetching-data$', DataImporterRunFetchingData.as_view(), name='data-importer-schedule-fetching-data'),
    url(r'^monitor-rate-limit$', DataImporterMonitorRateLimits.as_view(), name='monitor-rate-limit'),
)
