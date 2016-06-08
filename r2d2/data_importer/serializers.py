# -*- coding: utf-8 -*-
from r2d2.data_importer.models import SourceSuggestion
from r2d2.utils.serializers import R2D2ModelSerializer
from r2d2.utils.serializers import R2D2Serializer


class DataImporterAccountSerializer(R2D2Serializer):
    """ generic data importer serializer - proxy for data importer subclass serializers """

    def to_representation(self, obj):
        serializer_class = obj.get_serializer()
        serializer = serializer_class(obj)
        representation = serializer.to_representation(obj)
        representation['class'] = obj.__class__.__name__
        return representation


class SourceSuggestionSerializer(R2D2ModelSerializer):
    """ serializer for source suggestion """

    class Meta:
        model = SourceSuggestion
        fields = ['pk', 'text']
