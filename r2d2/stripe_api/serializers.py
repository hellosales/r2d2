# -*- coding: utf-8 -*-
""" stripe serializers """
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _
from rest_framework import serializers

from r2d2.data_importer.api import DataImporter
from r2d2.stripe_api.models import StripeAccount
from r2d2.utils.serializers import R2D2ModelSerializer
from r2d2.utils.serializers import R2D2Serializer


class StripeAccountSerializer(R2D2ModelSerializer):
    """ serializer for stripe store """
    code = serializers.CharField(required=False, write_only=True)

    class Meta:
        model = StripeAccount

        fields = ['pk', 'name', 'authorization_date', 'last_successfull_call', 'is_active', 'next_sync', 'last_updated',
                  'fetch_status', 'created', 'code', 'official_channel_name']
        read_only_fields = ['pk', 'authorization_date', 'last_successfull_call', 'next_sync', 'last_updated',
                            'fetch_status', 'created', 'official_channel_name']

    def validate(self, validated_data):
        errors = {}
        name = validated_data.get('name')
        code = validated_data.pop('code', None)

        # check name
        if not DataImporter.check_name_uniqeness(self.context['request'].user, name, self.instance):
            errors['name'] = [_(StripeAccount.NAME_NOT_UNIQUE_ERROR)]

        # if code is present - get the access_token
        if code:
            access_token, merchant_id, refresh_token = StripeAccount.get_access_token(code)
            if access_token:
                validated_data['access_token'] = access_token
                validated_data['the_refresh_token'] = refresh_token
                validated_data['merchant_id'] = merchant_id
                validated_data['authorization_date'] = timezone.now()
                # cleaning up state
                validated_data['fetch_status'] = StripeAccount.FETCH_IDLE
            else:
                errors['code'] = [_(StripeAccount.OAUTH_ERROR)]
        elif self.context['request'].method == 'POST':
            errors['code'] = [_('Fill in this field.')]

        if errors:
            for oneT, oneL in errors.items():
                outStr = ''
                for oneE in oneL:
                    outStr += oneE._proxy____args[0]
            raise serializers.ValidationError(errors)

        return validated_data


class StripeOauthUrlSerializer(R2D2Serializer):
    def to_representation(self, obj):
        return {
            'oauth_url': StripeAccount.authorization_url()
        }
