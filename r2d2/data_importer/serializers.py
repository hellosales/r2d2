# -*- coding: utf-8 -*-
from rest_framework import serializers


class DataImporterAccountSerializer(serializers.Serializer):
    """ generic data importer serializer - proxy for data importer subclass serializers """

    def to_representation(self, obj):
        serializer_class = obj.get_serializer()
        serializer = serializer_class(obj)
        representation = serializer.to_representation(obj)
        representation['class'] = obj.__class__.__name__
        return representation
