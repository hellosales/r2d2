# -*- coding: utf-8 -*-
""" stripe admin """
from django.contrib import admin
from django_mongoengine.admin_support.decorators import dynamic_fields_list_display

from r2d2.data_importer.admin import DataImporterAdmin
from r2d2.stripe_api.models import ImportedStripeOrder
from r2d2.stripe_api.models import StripeErrorLog
from r2d2.stripe_api.models import StripeAccount
from r2d2.utils.documents import StorageDocumentAdmin


class StripeErrorAdmin(admin.TabularInline):
    model = StripeErrorLog
    extra = 0
    readonly_fields = ('created_at', 'error', 'error_description')
    ordering = ('-created_at', )

    def has_add_permission(self, request):
        return False


class StripeAccountAdmin(DataImporterAdmin):
    inlines = [StripeErrorAdmin]

    def get_readonly_fields(self, request, obj=None):
        readonly_fields = super(StripeAccountAdmin, self).get_readonly_fields(request, obj)
        return readonly_fields + ('name',)


# TODO
@dynamic_fields_list_display('id', 'total_price', 'email', 'created_at')
class StripeOrderAdmin(StorageDocumentAdmin):
    pass


admin.site.register(StripeAccount, StripeAccountAdmin)
admin.site.register(ImportedStripeOrder, StripeOrderAdmin)
