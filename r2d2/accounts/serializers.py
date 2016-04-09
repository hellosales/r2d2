from rest_framework import serializers

from django.utils.translation import ugettext_lazy as _
from django.utils.encoding import force_text
from django.utils.http import urlsafe_base64_decode
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth import authenticate

from r2d2.accounts.models import (
    Account
)
from r2d2.accounts.validators import password_validator


class AccountSerializer(serializers.ModelSerializer):
    merchant_name = serializers.CharField(required=True)

    class Meta:
        model = Account
        fields = [
            'id',
            'first_name',
            'last_name',
            'email',
            'token',
            'merchant_name'
        ]
        read_only_fields = ['id']


class AuthSerializer(serializers.Serializer):
    email = serializers.CharField()
    password = serializers.CharField()

    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')

        if email and password:
            user = authenticate(email=email, password=password)

            if user and not user.is_active:
                msg = _('User is not active.')
                raise serializers.ValidationError(msg)
            if user:
                attrs['user'] = user
                return attrs
            else:
                msg = _('Unable to log in with provided credentials.')
                raise serializers.ValidationError(msg)
        else:
            msg = _('Must include "username" and "password"')
            raise serializers.ValidationError(msg)
        return attrs


class ResetPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField()


class ResetPasswordConfirmSerializer(serializers.Serializer):
    user_id = serializers.CharField()
    token = serializers.CharField()
    new_password = serializers.CharField(validators=[password_validator])
    re_new_password = serializers.CharField(validators=[password_validator])

    def validate(self, data):
        if data.get('new_password') != data.get('re_new_password'):
            raise serializers.ValidationError(_("Passwords do not match"))

        model = Account
        try:
            # urlsafe_base64_decode() decodes to bytestring on Python 3
            uid = force_text(urlsafe_base64_decode(data.get('user_id')))
            user = model._default_manager.get(pk=uid)
        except (TypeError, ValueError, OverflowError, model.DoesNotExist):
            user = None

        if user is not None and default_token_generator.check_token(user, data.get('token')):
            self.user = user
            return data
        raise serializers.ValidationError(_("Token is not valid"))


class RegisterSerializer(serializers.ModelSerializer):
    merchant_name = serializers.CharField(required=True)
    first_name = serializers.CharField(required=True)
    last_name = serializers.CharField(required=True)
    confirm_password = serializers.CharField(allow_blank=False, write_only=True)

    class Meta:
        model = Account
        fields = ('first_name', 'last_name', 'email', 'password', 'merchant_name', 'confirm_password')
        write_only_fields = ('password',)

    def validate(self, validated_data):
        password = validated_data.get('password')
        confirm_password = validated_data.get('confirm_password')
        if password != confirm_password:
            raise serializers.ValidationError({'confirm_password': _('Password should match')})

        return validated_data

    def create(self, validated_data):
        validated_data.pop('confirm_password')
        user = super(RegisterSerializer, self).create(validated_data)
        user.set_password(validated_data['password'])
        user.save()
        return user
