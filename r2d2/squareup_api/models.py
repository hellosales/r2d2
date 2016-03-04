# -*- coding: utf-8 -*-
""" etsy models """
import requests

from django.conf import settings
from django.db import models
from django.utils import timezone

from r2d2.accounts.models import Account

AUTHORIZATION_ENDPOINT = 'https://connect.squareup.com/oauth2/authorize?client_id=%s'
ACCESS_TOKEN_ENDPOINT = 'https://connect.squareup.com/oauth2/token'


class SquareupAccount(models.Model):
    """ model for storing connection between squareup account and user,
        each user may be connected with many accounts,

        Since squareup does not allow custom callback & there is no other identification
        of the request, we need to mark model that is in authroization, so we can retrive it
        on callback. This is the reason for 'in_authrization' flag. Setting this flag unsettle
        it for any other SquareupAccount for given user.

        Trying to authorize two account simultaneously for one user will end up a mess.

        This model keeps also token if the user authorized our app to use this account"""
    user = models.ForeignKey(Account)
    name = models.CharField(max_length=255, db_index=True)
    access_token = models.CharField(max_length=255, null=True, blank=True)
    in_authorization = models.BooleanField(default=True) # on creation we assume authroization
    authorization_date = models.DateTimeField(null=True, blank=True)
    last_successfull_call = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = ('user', 'name')
        ordering = ('name', )

    def save(self, *args, **kwargs):
        super(SquareupAccount, self).save(*args, **kwargs)
        if self.in_authorization:
            SquareupAccount.objects.filter(user=self.user).exclude(pk=self.pk).update(in_authorization=False)

    @property
    def is_authorized(self):
        """ if token is set we assume account is authorized """
        return bool(self.access_token)

    @property
    def authorization_url(self):
        """ getting authorization url for the account """
        if self.is_authorized or not self.in_authorization:
            return None

        if not hasattr(self, '_authorization_url'):
            self._authorization_url = AUTHORIZATION_ENDPOINT%settings.SQUAREUP_API_KEY

        return self._authorization_url

    def get_access_token(self, authorization_code):
        request_data = {
          'client_id': settings.SQUAREUP_API_KEY,
          'client_secret': settings.SQUAREUP_API_SECRET,
          'code': authorization_code
        }

        response = requests.post(ACCESS_TOKEN_ENDPOINT, request_data)
        data = response.json()

        if 'access_token' in data and data['access_token']:
            self.access_token = data['access_token']
            self.in_authorization = False
            self.authorization_date = timezone.now()
            self.save()
            return True
        return False

    def __unicode__(self):
        return self.name

