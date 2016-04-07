# -*- coding: utf-8 -*-
""" squareup serializers """
from django.utils.translation import ugettext_lazy as _
from rest_framework import serializers

from r2d2.squareup_api.models import SquareupAccount


class SquareupAccountSerializer(serializers.ModelSerializer):
    """ serializer for squareup store """
    class Meta:
        model = SquareupAccount

        fields = ['pk', 'name', 'access_token', 'authorization_date', 'last_successfull_call', 'is_authorized',
                  'in_authorization', 'authorization_url']
        read_only_fields = ['pk', 'authorization_date', 'last_successfull_call', 'is_authorized', 'in_authorization',
                            'authorization_url']

    def validate(self, validated_data):
        name = validated_data.get('name')
        query = SquareupAccount.objects.filter(name=name, user=self.context['request'].user)
        if self.instance:
            query = query.exclude(pk=self.instance.pk)
        if query.exists():
            raise serializers.ValidationError({'name': _('Name must be uniqe')})

        return validated_data
