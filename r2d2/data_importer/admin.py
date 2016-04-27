# -*- coding: utf-8 -*-
""" base admin for data importer submodels """
from django.contrib import admin

from r2d2.data_importer.api import DataImporter


class DataImporterAdmin(admin.ModelAdmin):
    list_display = ('name', 'user', 'is_authorized', 'fetch_status', 'fetch_scheduled_at', 'last_successfull_call')
    readonly_fields = ('authorization_date', 'last_successfull_call', 'last_error', 'last_api_items_dates',
                       'fetch_scheduled_at', 'access_token', 'user')

    def force_fetching_action(self, request, queryset):
        for item in queryset:
            if item.is_authorized:
                DataImporter.create_import_task(item.__class__, item.pk)
    force_fetching_action.short_description = "force fetching data"

    actions = ['force_fetching_action']
