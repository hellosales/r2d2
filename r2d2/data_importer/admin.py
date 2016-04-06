# -*- coding: utf-8 -*-
""" base admin for data importer submodels """
from django.contrib import admin


class DataImporterAdmin(admin.ModelAdmin):
    list_display = ('name', 'user', 'is_authorized', 'fetch_status', 'fetch_scheduled_at', 'last_successfull_call')
    readonly_fields = ('authorization_date', 'last_successfull_call', 'last_error', 'last_api_items_dates',
                       'fetch_scheduled_at', 'access_token', 'user')
