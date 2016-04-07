# -*- coding: utf-8 -*-
""" shopify models """
import shopify

from constance import config
from django.conf import settings
from django.core.urlresolvers import reverse

from r2d2.data_importer.api import DataImporter
from r2d2.data_importer.models import AbstractDataProvider
from r2d2.utils.documents import StorageDynamicDocument


class ShopifyStore(AbstractDataProvider):
    """ model for storing connection between store and user,
        each user may be connected with many stores,
        each store may be connected with many users [unsure if one user will not log out the other]
        however pair (store, user) should be unique.

        this model keeps also token if the user authorized
        our app to use this account"""
    MAX_REQUEST_LIMIT = 250

    @classmethod
    def get_serializer(cls):
        from r2d2.shopify_api.serializers import ShopifyStoreSerializer
        return ShopifyStoreSerializer

    @property
    def authorization_url(self):
        """ getting authorization url for the store """
        if self.is_authorized:
            return None

        if not hasattr(self, '_authorization_url'):
            callback_link = '%s://%s%s' % ('https' if getattr(settings, 'IS_SECURE', False) else 'http',
                                           config.CLIENT_DOMAIN, reverse('shopify-callback'))
            shopify.Session.setup(api_key=settings.SHOPIFY_API_KEY, secret=settings.SHOPIFY_API_SECRET)
            session = shopify.Session(self._store_url)
            self._authorization_url = session.create_permission_url(settings.SHOPIFY_SCOPES, callback_link)

        return self._authorization_url

    @property
    def _store_url(self):
        return "%s.myshopify.com" % self.name

    def _activate_session(self):
        assert self.is_authorized
        session = shopify.Session(self._store_url, self.access_token)
        shopify.ShopifyResource.activate_session(session)
        return session

    def _import_orders(self, updated_after=None, min_id=None):
        """ return orders, returns True if there are more items to query """
        kwargs = {'status': 'any', 'limit': self.MAX_REQUEST_LIMIT}
        if updated_after:
            kwargs['updated_at_min'] = updated_after
        if min_id:
            kwargs['since_id'] = min_id

        max_id = 0
        max_updated_at = ''
        orders = shopify.Order.find(**kwargs)
        for order in orders:
            # if objects with given ID already exists - we delete it and create a new one (it was updated, so we want
            # just to replace it)
            ImportedShopifyOrder.objects.filter(shopify_id=order['id']).delete()
            ImportedShopifyOrder.create_from_json(self, order)
            self.last_api_items_dates['order'] = order['updated_at']
            self.save()
            max_id = max(max_id, order['id'])
            max_updated_at = max(max_updated_at, order['updated_at'])
        return len(orders) == self.MAX_REQUEST_LIMIT, max_updated_at, max_id

    def _fetch_data_inner(self):
        self._activate_session()
        last_updated = self.last_api_items_dates.get('order', None)
        has_more = True
        if last_updated:
            while has_more:
                has_more, last_updated, dummy = self._import_orders(updated_after=last_updated)
        else:
            # first import path
            min_id = None
            while has_more:
                has_more, dummy, max_id = self._import_orders(min_id=min_id)
                min_id = max_id + 1

    def __unicode__(self):
        return self.name

DataImporter.register(ShopifyStore)


class ImportedShopifyOrder(StorageDynamicDocument):
    account_model = ShopifyStore
    prefix = "shopify"
