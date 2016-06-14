# -*- coding: utf-8 -*-
""" shopify models """
import shopify

from constance import config
from decimal import Decimal

from django.conf import settings
from django.db import models

from r2d2.common_layer.signals import object_imported
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
    store_url = models.URLField()
    MAX_REQUEST_LIMIT = 250

    def save(self, *args, **kwargs):
        super(ShopifyStore, self).save(*args, **kwargs)
        # it is no longer possible to save unauthorized account
        self.user.data_importer_account_authorized()

    @classmethod
    def get_serializer(cls):
        from r2d2.shopify_api.serializers import ShopifyStoreSerializer
        return ShopifyStoreSerializer

    @classmethod
    def get_oauth_url_serializer(cls):
        from r2d2.shopify_api.serializers import ShopifyOauthUrlSerializer
        return ShopifyOauthUrlSerializer

    @classmethod
    def authorization_url(cls, store_slug):
        """ getting authorization url for the store """
        callback_link = '%s://%s%s' % ('https' if getattr(settings, 'IS_SECURE', False) else 'http',
                                       config.CLIENT_DOMAIN, settings.SHOPIFY_CALLBACK_ENDPOINT)
        shopify.Session.setup(api_key=settings.SHOPIFY_API_KEY, secret=settings.SHOPIFY_API_SECRET)
        session = shopify.Session(cls._store_url(store_slug))
        return session.create_permission_url(settings.SHOPIFY_SCOPES, callback_link)

    @classmethod
    def get_access_token(cls, shop, code, timestamp, signature, hmac):
        params = {'shop': shop, 'code': code, 'timestamp': timestamp, 'signature': signature, 'hmac': hmac}
        shopify.Session.setup(api_key=settings.SHOPIFY_API_KEY, secret=settings.SHOPIFY_API_SECRET)
        session = shopify.Session(shop)

        try:
            return session.request_token(params)
        except:  # shopify can throw here general exception
            return None

    @classmethod
    def _store_url(cls, store_slug):
        return "%s.myshopify.com" % store_slug

    def map_data(self, imported_shopify_order):
        mapped_data = {
            'user_id': self.user_id,
            'transaction_id': imported_shopify_order.shopify_id,
            'date': imported_shopify_order.created_at,
            'total_price': Decimal(imported_shopify_order.total_line_items_price),
            'total_tax': Decimal(imported_shopify_order.total_tax),
            'total_discount': Decimal(imported_shopify_order.total_discounts),
            'total_total': Decimal(imported_shopify_order.total_price),
            'products': []
        }

        for item in imported_shopify_order.line_items:
            mapped_product = {
                'name': item['title'],
                'sku': item['sku'],
                'quantity': Decimal(item['quantity']),
                'price': Decimal(item['price']),
                'tax': Decimal(0),
                'discount': Decimal(item['total_discount']),
                'total': Decimal(0)
            }
            for line in item['tax_lines']:
                mapped_product['tax'] += Decimal(line['price'])
            mapped_product['total'] = mapped_product['price'] - mapped_product['discount'] + mapped_product['tax']
            mapped_data['products'].append(mapped_product)

        return mapped_data

    def _activate_session(self):
        session = shopify.Session(self.store_url, self.access_token)
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
            order = order.to_dict()
            ImportedShopifyOrder.objects.filter(shopify_id=order['id'], account_id=self.id).delete()
            imported_shopify_order = ImportedShopifyOrder.create_from_json(self, order)
            self.last_api_items_dates['order'] = order['updated_at']
            self.save()
            max_id = max(max_id, order['id'])
            max_updated_at = max(max_updated_at, order['updated_at'])

            # mapping data & sending it out
            mapped_data = self.map_data(imported_shopify_order)
            object_imported.send(sender=None, importer_account=self, mapped_data=mapped_data)
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
