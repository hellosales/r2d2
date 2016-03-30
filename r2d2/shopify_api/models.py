# -*- coding: utf-8 -*-
""" shopify models """
import shopify

from constance import config

from django.conf import settings
from django.core.urlresolvers import reverse
from django.db import models
from django_mongoengine import document

from r2d2.accounts.models import Account


class ShopifyStore(models.Model):
    """ model for storing connection between store and user,
        each user may be connected with many stores,
        each store may be connected with many users [unsure if one user will not log out the other]
        however pair (store, user) should be unique.

        this model keeps also token if the user authorized
        our app to use this account"""
    user = models.ForeignKey(Account)
    name = models.SlugField(max_length=255, db_index=True)
    access_token = models.CharField(max_length=255, null=True, blank=True)
    authorization_date = models.DateTimeField(null=True, blank=True)
    last_successfull_call = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = ('user', 'name')
        ordering = ('name', )

    @property
    def is_authorized(self):
        """ if token is set we assume store is authorized """
        return bool(self.access_token)

    @property
    def authorization_url(self):
        """ getting authorization url for the store """
        if self.is_authorized:
            return None

        if not hasattr(self, '_authorization_url'):
            callback_link = '%s://%s%s' % ('https' if getattr(settings, 'IS_SECURE', False) else 'http',
                                           config.CLIENT_DOMAIN, reverse('shopify-callback'))
            shopify.Session.setup(api_key=settings.SHOPIFY_API_KEY, secret=settings.SHOPIFY_API_SECRET)
            session = shopify.Session("%s.myshopify.com" % self.name)
            self._authorization_url = session.create_permission_url(settings.SHOPIFY_SCOPES, callback_link)

        return self._authorization_url

    def __unicode__(self):
        return self.name


class ShopifyOrder(document.DynamicDocument):
    pass
