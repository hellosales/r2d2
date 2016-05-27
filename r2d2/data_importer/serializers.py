# -*- coding: utf-8 -*-
from rest_framework import serializers

from r2d2.data_importer.models import SourceSuggestion


class DataImporterAccountSerializer(serializers.Serializer):
    """ generic data importer serializer - proxy for data importer subclass serializers """

    def to_representation(self, obj):
        serializer_class = obj.get_serializer()
        serializer = serializer_class(obj)
        representation = serializer.to_representation(obj)
        representation['class'] = obj.__class__.__name__
        return representation


class SourceSuggestionSerializer(serializers.ModelSerializer):
    """ serializer for source suggestion """

    class Meta:
        model = SourceSuggestion
        fields = ['pk', 'text']
