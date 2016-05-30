# -*- coding: utf-8 -*-
""" etsy API urls """
from django.conf.urls import patterns
from django.conf.urls import url

from r2d2.data_importer.api import DataImporterAccountsAPI
from r2d2.data_importer.api import SuggestionCreateAPI


urlpatterns = patterns(
    '',
    url(r'^accounts$', DataImporterAccountsAPI.as_view(), name='data-importer-accounts'),
    url(r'^source-sugesstions$', SuggestionCreateAPI.as_view(), name='source-suggestions-api'),
)
