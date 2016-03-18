# -*- coding: utf-8 -*-
""" etsy serializers """
from rest_framework import serializers

from r2d2.etsy_api.models import EtsyAccount


class EtsyAccountSerializer(serializers.ModelSerializer):
    """ serializer for etsy account """
    class Meta:
        model = EtsyAccount

        fields = ['pk', 'name', 'access_token', 'authorization_date', 'last_successfull_call', 'is_authorized',
                  'authorization_url']
        read_only_fields = ['pk', 'authorization_date', 'last_successfull_call', 'is_authorized', 'authorization_url']
