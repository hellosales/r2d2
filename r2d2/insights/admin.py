# -*- coding: utf-8 -*-
from django.contrib import admin

from r2d2.insights.models import Insight
from r2d2.insights.models import InsightAttachment


class InsightAttachmentAdmin(admin.StackedInline):
    model = InsightAttachment
    extra = 1
    readonly_fields = ('content_type', )


class InsightAdmin(admin.ModelAdmin):
    list_display = ('user', 'created', 'text', 'generator_class')
    inlines = [InsightAttachmentAdmin]

    def save_model(self, request, obj, form, change):
        if not obj.generator_class:
            obj.generator_class = "Manual"
        obj.save()


admin.site.register(Insight, InsightAdmin)
