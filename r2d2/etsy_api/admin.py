# -*- coding: utf-8 -*-
""" etsy models admin """
from django.contrib import admin

from r2d2.etsy_api.models import EtsyAccount


class EtsyAccountAdmin(admin.ModelAdmin):
    list_display = ('name', 'user', 'is_authorized')


admin.site.register(EtsyAccount, EtsyAccountAdmin)
