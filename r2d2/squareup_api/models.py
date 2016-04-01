# -*- coding: utf-8 -*-
""" etsy models """
import requests

from dateutil.parser import parse as parse_date
from django.conf import settings
from django.db import models
from django.utils import timezone

from r2d2.data_importer.api import DataImporter
from r2d2.data_importer.models import AbstractDataProvider


class SquareupAccount(AbstractDataProvider):
    """ model for storing connection between squareup account and user,
        each user may be connected with many accounts,

        Since squareup does not allow custom callback & there is no other identification
        of the request, we need to mark model that is in authroization, so we can retrive it
        on callback. This is the reason for 'in_authrization' flag. Setting this flag unsettle
        it for any other SquareupAccount for given user.

        Trying to authorize two account simultaneously for one user will end up a mess.

        This model keeps also token if the user authorized our app to use this account"""
    in_authorization = models.BooleanField(default=True)  # on creation we assume authroization
    token_expiration = models.DateTimeField(null=True, blank=True, db_index=True)
    merchant_id = models.CharField(max_length=255, null=True, blank=True)

    def save(self, *args, **kwargs):
        super(SquareupAccount, self).save(*args, **kwargs)
        if self.in_authorization:
            SquareupAccount.objects.filter(user=self.user).exclude(pk=self.pk).update(in_authorization=False)

    @property
    def authorization_url(self):
        """ getting authorization url for the account """
        if self.is_authorized or not self.in_authorization:
            return None

        if not hasattr(self, '_authorization_url'):
            self._authorization_url = settings.SQUAREUP_AUTHORIZATION_ENDPOINT % settings.SQUAREUP_API_KEY

        return self._authorization_url

    def _save_token(self, data):
        """ save token from json data """
        if 'access_token' in data and data['access_token']:
            self.access_token = data['access_token']
            self.in_authorization = False
            self.merchant_id = data.get('merchant_id', '')
            if 'expires_at' in data and data['expires_at']:
                self.token_expiration = parse_date(data['expires_at'])
            self.authorization_date = timezone.now()
            self.save()
            return True
        return False

    def get_access_token(self, authorization_code):
        """ obtain access_token using authorization code """
        request_data = {
          'client_id': settings.SQUAREUP_API_KEY,
          'client_secret': settings.SQUAREUP_API_SECRET,
          'code': authorization_code
        }

        response = requests.post(settings.SQUAREUP_ACCESS_TOKEN_ENDPOINT, request_data)
        if response.status_code == 200:
            return self._save_token(response.json())
        return False

    def refresh_token(self):
        """ refresh token """
        if self.access_token:
            response = requests.post(
                settings.SQUAREUP_RENEW_TOKEN_ENDPOINT % settings.SQUAREUP_API_KEY,
                {'access_token': self.access_token},
                headers={'Authorization': 'Client %s' % settings.SQUAREUP_API_SECRET}
            )
            if response.status_code == 200:
                return self._save_token(response.json())

    def _fetch_data_inner(self):
        pass  # TODO

    def __unicode__(self):
        return self.name


DataImporter.register(SquareupAccount)
