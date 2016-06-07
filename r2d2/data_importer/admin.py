# -*- coding: utf-8 -*-
""" base admin for data importer submodels """
from django.contrib import admin

from r2d2.data_importer.api import DataImporter
from r2d2.data_importer.models import SourceSuggestion


class DataImporterAdmin(admin.ModelAdmin):
    list_display = ('name', 'created', 'user', 'is_authorized', 'fetch_status', 'fetch_scheduled_at',
                    'last_successfull_call')
    readonly_fields = ('authorization_date', 'last_successfull_call', 'last_error', 'last_api_items_dates',
                       'fetch_scheduled_at', 'access_token', 'user')

    def has_add_permission(self, request):
        return False

    def force_fetching_action(self, request, queryset):
        for item in queryset:
            if item.is_authorized:
                DataImporter.create_import_task(item.__class__, item.pk)
    force_fetching_action.short_description = "force fetching data"

    actions = ['force_fetching_action']


class SourceSuggestionAdmin(admin.ModelAdmin):
    list_display = ('user', 'text')
    readonly_fields = ('user', 'text')


admin.site.register(SourceSuggestion, SourceSuggestionAdmin)
