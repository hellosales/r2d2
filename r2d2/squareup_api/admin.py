# -*- coding: utf-8 -*-
""" squareup admin """
from django.contrib import admin

from r2d2.squareup_api.models import SquareupAccount


class SquareupAccountAdmin(admin.ModelAdmin):
    """ squareup model admin """
    list_display = ('name', 'user', 'is_authorized')


admin.site.register(SquareupAccount, SquareupAccountAdmin)
