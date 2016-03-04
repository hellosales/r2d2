# -*- coding: utf-8 -*-
""" etsy serializers """
from rest_framework import serializers

from r2d2.etsy_api.models import EtsyAccount


class EtsyAccountSerializer(serializers.ModelSerializer):
    """ serializer for shopify store """
    class Meta:
        model = EtsyAccount

        fields = ['id', 'name', 'authorization_date', 'last_successfull_call', 'is_authorized', 'authorization_url']
        read_only_fields = ['id', 'authorization_date', 'last_successfull_call', 'is_authorized', 'authorization_url']

