# -*- coding: utf-8 -*-
""" shopify serializers """
from rest_framework import serializers

from r2d2.shopify_api.models import ShopifyStore


class ShopifyStoreSerializer(serializers.ModelSerializer):
    """ serializer for shopify store """
    class Meta:
        model = ShopifyStore

        fields = ['pk', 'name', 'access_token', 'authorization_date', 'last_successfull_call', 'is_authorized',
                  'authorization_url']
        read_only_fields = ['pk', 'authorization_date', 'last_successfull_call', 'is_authorized', 'authorization_url']
