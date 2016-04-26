# -*- coding: utf-8 -*-
""" insights serializers """
from rest_framework import serializers

from r2d2.insights.models import Insight


class InsightSerializer(serializers.ModelSerializer):
    """ serializer for insights """
    class Meta:
        model = Insight
        read_only_fields = fields = ['pk', 'created', 'text']
