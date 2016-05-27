# -*- coding: utf-8 -*-
from django.contrib import admin

from r2d2.insights.models import Insight
from r2d2.insights.models import InsightAttachment


class InsightAttachmentAdmin(admin.StackedInline):
    model = InsightAttachment
    extra = 1


class InsightAdmin(admin.ModelAdmin):
    list_display = ('user', 'created', 'text', 'generator_class')
    inlines = [InsightAttachmentAdmin]


admin.site.register(Insight, InsightAdmin)
