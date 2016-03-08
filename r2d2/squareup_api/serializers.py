# -*- coding: utf-8 -*-
""" squareup serializers """
from rest_framework import serializers

from r2d2.squareup_api.models import SquareupAccount


class SquareupAccountSerializer(serializers.ModelSerializer):
    """ serializer for squareup store """
    class Meta:
        model = SquareupAccount

        fields = ['id', 'name', 'authorization_date', 'last_successfull_call', 'is_authorized', 'in_authorization',
                  'authorization_url']
        read_only_fields = ['id', 'authorization_date', 'last_successfull_call', 'is_authorized', 'in_authorization',
                            'authorization_url']
