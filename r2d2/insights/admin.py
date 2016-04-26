# -*- coding: utf-8 -*-
from django.contrib import admin

from r2d2.insights.models import Insight


class InsightAdmin(admin.ModelAdmin):
    list_display = ('user', 'created', 'text', 'generator_class')


admin.site.register(Insight, InsightAdmin)
