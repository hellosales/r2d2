# -*- coding: utf-8 -*-
""" shopify serializers """
from django.utils.translation import ugettext_lazy as _
from rest_framework import serializers

from r2d2.shopify_api.models import ShopifyStore


class ShopifyStoreSerializer(serializers.ModelSerializer):
    """ serializer for shopify store """
    class Meta:
        model = ShopifyStore

        fields = ['pk', 'name', 'access_token', 'authorization_date', 'last_successfull_call', 'is_authorized',
                  'authorization_url', 'is_active', 'next_sync', 'last_updated', 'fetch_status']
        read_only_fields = ['pk', 'authorization_date', 'last_successfull_call', 'is_authorized', 'authorization_url',
                            'next_sync', 'last_updated', 'fetch_status']

    def validate(self, validated_data):
        name = validated_data.get('name')
        query = ShopifyStore.objects.filter(name=name, user=self.context['request'].user)
        if self.instance:
            if self.instance.name != name:
                raise serializers.ValidationError({'name': _('Shopify store name cannot be changed.')})
            query = query.exclude(pk=self.instance.pk)
        if query.exists():
            raise serializers.ValidationError({'name': _('Name must be uniqe')})

        return validated_data
