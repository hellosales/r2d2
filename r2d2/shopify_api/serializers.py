# -*- coding: utf-8 -*-
""" shopify serializers """
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _
from rest_framework import serializers

from r2d2.shopify_api.models import ShopifyStore
from r2d2.utils.serializers import R2D2ModelSerializer
from r2d2.utils.serializers import R2D2Serializer


class ShopifyStoreSerializer(R2D2ModelSerializer):
    """ serializer for shopify store """
    shop = serializers.CharField(required=False, write_only=True)
    code = serializers.CharField(required=False, write_only=True)
    timestamp = serializers.CharField(required=False, write_only=True)
    signature = serializers.CharField(required=False, write_only=True)
    hmac = serializers.CharField(required=False, write_only=True)

    class Meta:
        model = ShopifyStore

        fields = ['pk', 'name', 'authorization_date', 'last_successfull_call', 'is_active', 'next_sync', 'last_updated',
                  'fetch_status', 'created', 'shop', 'code', 'timestamp', 'signature', 'hmac']
        read_only_fields = ['pk', 'authorization_date', 'last_successfull_call', 'next_sync', 'last_updated',
                            'fetch_status', 'created']

    def validate(self, validated_data):
        errors = {}
        name = validated_data.get('name')
        shop = validated_data.pop('shop', None)
        code = validated_data.pop('code', None)
        timestamp = validated_data.pop('timestamp', None)
        signature = validated_data.pop('signature', None)
        hmac = validated_data.pop('hmac', None)

        # check name
        query = ShopifyStore.objects.filter(name=name, user=self.context['request'].user)
        if self.instance:
            query = query.exclude(pk=self.instance.pk)
        if query.exists():
            errors['name'] = [_(ShopifyStore.NAME_NOT_UNIQUE_ERROR)]

        # if auth data is present - get the access_token
        if shop and code and timestamp and signature and hmac:
            access_token = ShopifyStore.get_access_token(shop, code, timestamp, signature, hmac)
            if access_token:
                validated_data['access_token'] = access_token
                validated_data['authorization_date'] = timezone.now()
                validated_data['store_url'] = shop
            else:
                errors['code'] = [_(ShopifyStore.OAUTH_ERROR)]
        elif self.context['request'].method == 'POST':
            if not shop:
                errors['shop'] = [_('Fill in this field.')]
            if not code:
                errors['code'] = [_('Fill in this field.')]
            if not timestamp:
                errors['timestamp'] = [_('Fill in this field.')]
            if not signature:
                errors['signature'] = [_('Fill in this field.')]
            if not hmac:
                errors['hmac'] = [_('Fill in this field.')]

        if errors:
            raise serializers.ValidationError(errors)

        return validated_data


class ShopifyOauthUrlSerializer(R2D2Serializer):
    shop_slug = serializers.SlugField(required=True)

    def to_representation(self, obj):
        return {
            'oauth_url': ShopifyStore.authorization_url(self.validated_data['shop_slug'])
        }
