# -*- coding: utf-8 -*-
from rest_framework import serializers

from django.contrib.auth import authenticate
from django.contrib.auth.tokens import default_token_generator
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.utils.encoding import force_text
from django.utils.http import urlsafe_base64_decode
from django.utils.translation import ugettext_lazy as _
from passwords.validators import complexity
from passwords.validators import validate_length


from r2d2.accounts.models import Account
from r2d2.accounts.validators import password_validator
from r2d2.utils.serializers import R2D2ModelSerializer
from r2d2.utils.serializers import R2D2Serializer


class AccountSerializer(R2D2ModelSerializer):
    EMAIL_ERROR = _('Your user name needs to be an email address. You will receive insights about your data and other '
                    'information at this address.')
    merchant_name = serializers.CharField(required=True)
    first_name = serializers.CharField(required=True)
    last_name = serializers.CharField(required=True)
    email = serializers.CharField(required=False)

    def validate_email(self, value):
        return value

    def validate(self, validated_data):
        errors = {}
        user = self.context['user']

        email = validated_data.get('email')
        if not email:
            errors['email'] = self.EMAIL_ERROR
        else:
            try:
                validate_email(email)
            except ValidationError:
                errors['email'] = self.EMAIL_ERROR

            if Account.objects.exclude(id=user.id).filter(email=email).exists():
                errors['email'] = _('This email is already in use')

        if errors:
            raise serializers.ValidationError(errors)

        return validated_data

    class Meta:
        model = Account
        fields = [
            'id',
            'first_name',
            'last_name',
            'email',
            'token',
            'merchant_name',
            'date_joined',
            'last_login'
        ]
        read_only_fields = ['id']


class AuthSerializer(R2D2Serializer):
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


class ResetPasswordSerializer(R2D2Serializer):
    email = serializers.EmailField()


class ResetPasswordConfirmSerializer(R2D2Serializer):
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
            # except (model.DoesNotExist):
            user = None

        if user is not None and default_token_generator.check_token(user, urlsafe_base64_decode(data.get('token'))):
            self.user = user
            return data
        raise serializers.ValidationError(_("Token is not valid"))


class ChangePasswordSerializer(R2D2Serializer):
    old_password = serializers.CharField(allow_blank=False)
    new_password = serializers.CharField(allow_blank=False)
    confirm_password = serializers.CharField(allow_blank=True)

    def validate(self, validated_data):
        errors = {}
        user = self.context['user']

        old_password = validated_data.get('old_password')
        new_password = validated_data.get('new_password')
        confirm_password = validated_data.get('confirm_password')

        if old_password and not user.check_password(old_password):
            errors['old_password'] = _('This password doesn’t match our records')

        if new_password:
            for v in [validate_length, complexity]:
                try:
                    v(new_password)
                except ValidationError:
                    errors['new_password'] = \
                        _('Your password must be 8 characters long and contain at least 1 number and 1 letter')
                    break

        if new_password != confirm_password:
            errors['confirm_password'] = _('Make sure this field is not blank and matches your password exactly')

        if errors:
            raise serializers.ValidationError(errors)

        return validated_data

    def update(self, instance, validated_data):
        instance.set_password(validated_data['new_password'])
        return instance


class RegisterSerializer(R2D2ModelSerializer):
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
