# -*- coding: utf-8 -*-
""" insights serializers """
import math

from django.utils.dateformat import DateFormat
from rest_framework import serializers

from r2d2.common_layer.models import CommonTransaction
from r2d2.etsy_api.models import EtsyAccount
from r2d2.insights.models import Insight
from r2d2.insights.models import InsightAttachment
from r2d2.shopify_api.models import ShopifyStore
from r2d2.squareup_api.models import SquareupAccount
from r2d2.utils.serializers import R2D2ModelSerializer
from r2d2.utils.serializers import R2D2Serializer


class InsightAttachmentSerializer(R2D2ModelSerializer):
    class Meta:
        model = InsightAttachment
        fields = ['pk', 'content_type', 'file', 'file_name']


class InsightSerializer(R2D2ModelSerializer):
    """ serializer for insights """
    created = serializers.SerializerMethodField()
    attachments = InsightAttachmentSerializer(many=True)

    def get_created(self, obj):
        return DateFormat(obj.created).format('N j').replace('.', '')

    class Meta:
        model = Insight
        read_only_fields = fields = ['pk', 'created', 'text', 'attachments']


class HeaderDataSerializer(R2D2Serializer):
    """ serializer for header data """
    channels_number = serializers.SerializerMethodField()
    insights_number = serializers.SerializerMethodField()
    transactions_number = serializers.SerializerMethodField()

    @classmethod
    def _format_number(cls, number):
        if number < 10000:
            return number
        elif number < 100000:
            return "%.1fK" % (math.floor((number / 100.0)) / 10.0)
        elif number < 1000000:
            return "%dK" % (number / 1000)
        else:
            return "%.1fM" % (math.floor((number / 100000.0)) / 10.0)

    def get_channels_number(self, obj):
        return EtsyAccount.objects.filter(user=obj).count() + ShopifyStore.objects.filter(user=obj).count() + \
            SquareupAccount.objects.filter(user=obj).count()

    def get_insights_number(self, obj):
        return Insight.objects.filter(user=obj).count()

    def get_transactions_number(self, obj):
        return self._format_number(CommonTransaction.objects.filter(user_id=obj.id).count())
