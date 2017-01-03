# -*- coding: utf-8 -*-
""" etsy serializers """
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _
from rest_framework import serializers

from r2d2.data_importer.api import DataImporter
from r2d2.etsy_api.models import EtsyAccount
from r2d2.utils.serializers import R2D2ModelSerializer
from r2d2.utils.serializers import R2D2Serializer


class EtsyAccountSerializer(R2D2ModelSerializer):
    """ serializer for etsy account """
    oauth_verifier = serializers.CharField(required=False, write_only=True)
    id = serializers.CharField(required=False, write_only=True)

    class Meta:
        model = EtsyAccount

        fields = ['pk', 'name', 'authorization_date', 'last_successfull_call', 'is_active', 'next_sync', 'last_updated',
                  'fetch_status', 'created', 'oauth_verifier', 'id', 'official_channel_name']
        read_only_fields = ['pk', 'authorization_date', 'last_successfull_call', 'next_sync', 'last_updated',
                            'fetch_status', 'created', 'official_channel_name']

    def validate(self, validated_data):
        errors = {}
        name = validated_data.get('name')
        oauth_verifier = validated_data.pop('oauth_verifier', None)
        request_id = validated_data.pop('id', None)

        # check name
        if not DataImporter.check_name_uniqeness(self.context['request'].user, name, self.instance):
            errors['name'] = [_(EtsyAccount.NAME_NOT_UNIQUE_ERROR)]

        # if oauth_verifier & request_id are present - get the access_token
        if oauth_verifier and request_id:
            access_token = EtsyAccount.get_access_token(oauth_verifier, request_id)
            if access_token:
                validated_data['access_token'] = access_token
                validated_data['authorization_date'] = timezone.now()
                # cleaning up state
                validated_data['fetch_status'] = EtsyAccount.FETCH_IDLE
            else:
                errors['code'] = [_(EtsyAccount.OAUTH_ERROR)]
        elif self.context['request'].method == 'POST':
            if not oauth_verifier:
                errors['oauth_verifier'] = [_('Fill in this field.')]
            if not request_id:
                errors['id'] = [_('Fill in this field.')]

        if errors:
            raise serializers.ValidationError(errors)

        return validated_data


class EtsyOauthUrlSerializer(R2D2Serializer):
    def to_representation(self, obj):
        return {
            'oauth_url': EtsyAccount.authorization_url()
        }
