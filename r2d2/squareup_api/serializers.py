# -*- coding: utf-8 -*-
""" squareup serializers """
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _
from rest_framework import serializers

from r2d2.data_importer.api import DataImporter
from r2d2.squareup_api.models import SquareupAccount
from r2d2.utils.serializers import R2D2ModelSerializer
from r2d2.utils.serializers import R2D2Serializer


class SquareupAccountSerializer(R2D2ModelSerializer):
    """ serializer for squareup store """
    code = serializers.CharField(required=False, write_only=True)

    class Meta:
        model = SquareupAccount

        fields = ['pk', 'name', 'authorization_date', 'last_successfull_call', 'is_active', 'next_sync', 'last_updated',
                  'fetch_status', 'created', 'code']
        read_only_fields = ['pk', 'authorization_date', 'last_successfull_call', 'next_sync', 'last_updated',
                            'fetch_status', 'created']

    def validate(self, validated_data):
        errors = {}
        name = validated_data.get('name')
        code = validated_data.pop('code', None)

        # check name
        if not DataImporter.check_name_uniqeness(self.context['request'].user, name, self.instance):
            errors['name'] = [_(SquareupAccount.NAME_NOT_UNIQUE_ERROR)]

        # if code is present - get the access_token
        if code:
            access_token, merchant_id, token_expiration = SquareupAccount.get_access_token(code)
            if access_token:
                validated_data['access_token'] = access_token
                validated_data['merchant_id'] = merchant_id
                validated_data['token_expiration'] = token_expiration
                validated_data['authorization_date'] = timezone.now()
                # cleaning up state
                validated_data['fetch_status'] = SquareupAccount.FETCH_IDLE
            else:
                errors['code'] = [_(SquareupAccount.OAUTH_ERROR)]
        elif self.context['request'].method == 'POST':
            errors['code'] = [_('Fill in this field.')]

        if errors:
            raise serializers.ValidationError(errors)

        return validated_data


class SquareupOauthUrlSerializer(R2D2Serializer):
    def to_representation(self, obj):
        return {
            'oauth_url': SquareupAccount.authorization_url()
        }
