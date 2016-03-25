# -*- coding: utf-8 -*-
""" etsy models """
from constance import config
from etsy.oauth import EtsyEnvProduction
from etsy.oauth import EtsyOAuthClient
from oauth2 import Token

from django.conf import settings
from django.core.urlresolvers import reverse
from django.db import models
from django.utils import timezone

from r2d2.data_importer.api import DataImporter
from r2d2.data_importer.models import AbstractDataProvider


class EtsyAccount(AbstractDataProvider):
    """ model for storing connection between etsy accounts and user

        this model keeps also token if the user authorized
        our app to use this account"""
    request_token = models.CharField(max_length=255, null=True, blank=True)

    @property
    def authorization_url(self):
        """ getting authorization url for the account & store request token """
        if self.is_authorized:
            return None

        if not hasattr(self, '_authorization_url'):
            client = EtsyOAuthClient(settings.ETSY_API_KEY, settings.ETSY_API_SECRET, etsy_env=EtsyEnvProduction())
            callback_link = '%s://%s%s?id=%d' % ('https' if getattr(settings, 'IS_SECURE', False) else 'http',
                                                 config.CLIENT_DOMAIN, reverse('etsy-callback'), self.id)
            self._authorization_url = client.get_signin_url(oauth_callback=callback_link)
            self.request_token = client.token.to_string()  # request token is required in callback
            self.save()

        return self._authorization_url

    def get_access_token(self, oauth_verifier):
        """ gets access token and stores it into the model """
        client = EtsyOAuthClient(settings.ETSY_API_KEY, settings.ETSY_API_SECRET, etsy_env=EtsyEnvProduction(),
                                 token=Token.from_string(self.request_token))
        token = client.get_access_token(oauth_verifier)
        if not token:
            return False

        self.access_token = token.to_string()
        self.authorization_date = timezone.now()
        self.save()
        return True

    def __unicode__(self):
        return self.name


DataImporter.register(EtsyAccount)
