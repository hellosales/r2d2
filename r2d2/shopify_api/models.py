# -*- coding: utf-8 -*-
""" shopify models """
import shopify

from constance import config

from django.conf import settings
from django.core.urlresolvers import reverse

from r2d2.data_importer.models import AbstractDataProvider


class ShopifyStore(AbstractDataProvider):
    """ model for storing connection between store and user,
        each user may be connected with many stores,
        each store may be connected with many users [unsure if one user will not log out the other]
        however pair (store, user) should be unique.

        this model keeps also token if the user authorized
        our app to use this account"""

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
