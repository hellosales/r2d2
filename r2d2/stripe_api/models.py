# -*- coding: utf-8 -*-
""" stripe models """
import urllib
import requests
import stripe

from decimal import Decimal
from datetime import datetime

from django.conf import settings
from django.db import models
from django.utils import timezone

from r2d2.common_layer.signals import object_imported
from r2d2.data_importer.api import DataImporter
from r2d2.data_importer.models import AbstractDataProvider
from r2d2.data_importer.models import AbstractErrorLog
from r2d2.utils.documents import StorageDynamicDocument


class StripeAccount(AbstractDataProvider):
    """ model for storing connection between store and user,
        each user may be connected with many stores,
        each store may be connected with many users [unsure if one user will not log out the other]
        however pair (store, user) should be unique.

        this model keeps also token if the user authorized
        our app to use this account"""

    merchant_id = models.CharField(max_length=255, blank=True)
    the_refresh_token = models.CharField(max_length=255, blank=True)
    MAX_REQUEST_LIMIT = 100

    def __init__(self, *args, **kwargs):
        super(StripeAccount, self).__init__(*args, **kwargs)
        self.official_channel_name = 'Stripe'

    def save(self, *args, **kwargs):
        super(StripeAccount, self).save(*args, **kwargs)
        # it is no longer possible to save unauthorized account
        self.user.data_importer_account_authorized()

    @classmethod
    def get_serializer(cls):
        from r2d2.stripe_api.serializers import StripeAccountSerializer
        return StripeAccountSerializer

    @classmethod
    def get_error_log_class(cls):
        return StripeErrorLog

    @classmethod
    def get_oauth_url_serializer(cls):
        from r2d2.stripe_api.serializers import StripeOauthUrlSerializer
        return StripeOauthUrlSerializer

    @classmethod
    def authorization_url(cls):
        """ getting authorization url for the store """
#        return settings.STRIPE_AUTHORIZATION_ENDPOINT % {'scope': settings.STRIPE_SCOPE,
#                                                         'client_id': settings.STRIPE_CLIENT_ID}
        params = {'scope': settings.STRIPE_SCOPE,
                  'client_id': settings.STRIPE_CLIENT_ID,
                  'response_type': settings.STRIPE_RESPONSE_TYPE}

        return settings.STRIPE_AUTHORIZATION_ENDPOINT + '?' + urllib.urlencode(params)

    @classmethod
    def get_access_token(cls, authorization_code):
        request_data = {'grant_type': 'authorization_code',
                        'code': authorization_code,
                        'scope': settings.STRIPE_SCOPE,
                        'client_secret': settings.STRIPE_API_KEY}

        response = requests.post(settings.STRIPE_ACCESS_TOKEN_ENDPOINT, request_data)

        if response.status_code == 200:
            data = response.json()
            if 'access_token' in data and data['access_token']:
                access_token = data['access_token']
                merchant_id = data.get('stripe_user_id', '')
                refresh_token = data.get('refresh_token')
                return access_token, merchant_id, refresh_token
        return None, None, None

    def refresh_token(self):
        """ refresh token """
        request_data = {'grant_type': 'refresh_token',
                        'scope': settings.STRIPE_SCOPE,
                        'client_secret': settings.STRIPE_API_KEY,
                        'refresh_token': self.refresh_token}

        if self.access_token:
            response = requests.post(settings.STRIPE_CALLBACK_ENDPOINT, request_data)

            if response.status_code == 200:
                data = response.json()
                if 'access_token' in data and data['access_token']:
                    self.access_token = data['access_token']
                    self.merchant_id = data.get('stripe_user_id', '')
                    self.refresh_token = data.get('refresh_token')
                    self.authorization_date = timezone.now()
                    self.save()
                    self.user.data_importer_account_authorized()

    def map_data(self, imported_stripe_order):
        """
        Maps JSON Order data to a common representation for our own use
        """
        if imported_stripe_order['currency'].lower() == 'USD'.lower():  # Stripe uses lower, we use upper
            net_sales_divisor = 100
        else:
            net_sales_divisor = 1

        mapped_data = {
            'user_id': self.user_id,
            'transaction_id': imported_stripe_order.stripe_id,
            'date': datetime.fromtimestamp(imported_stripe_order['created']),
            'total_price': Decimal(imported_stripe_order['amount'])/net_sales_divisor,
            'total_total': 0,  # Calculated at the end
            'currency_code': imported_stripe_order['currency'].upper(),  # Stripe uses lower, we use upper
            'products': []
        }

        tax = Decimal(0)
        discount = Decimal(0)

        for item in imported_stripe_order.items:
            if item['type'] == 'sku':
                mapped_product = {
                                  'name': item['description'],
                                  'sku': item['parent'],
                                  'quantity': Decimal(item['quantity']),
                                  'price': Decimal(item['amount'])/net_sales_divisor,
                                  'tax': Decimal(0)/net_sales_divisor,
                                  'discount': Decimal(0)/net_sales_divisor,
                                  'total': Decimal(item['amount'])/net_sales_divisor}

                mapped_data['products'].append(mapped_product)
            elif item['type'] == 'tax':
                tax += Decimal(item['amount'])/net_sales_divisor
            elif item['type'] == 'discount':
                discount += Decimal(item['amount'])/net_sales_divisor
            # elif item['type'] == 'shipping':

        mapped_data['total_tax'] = tax/net_sales_divisor
        mapped_data['total_discount'] = discount/net_sales_divisor
        mapped_data['total_total'] = (mapped_data['total_price'] + mapped_data['total_tax'] -
                                      mapped_data['total_discount'])

        return mapped_data

    def _import_orders(self, starting_after=None):
        """
        Imports all orders starting after the passed order_id, or all orders
        available if no order_id is passed
        """
        max_updated_id = self.last_api_items_dates.get('order_id', None)
        max_updated_at = self.last_api_items_dates.get('order_created', None)

        stripe_response = self._call_fetch_orders(settings.STRIPE_API_KEY, self.MAX_REQUEST_LIMIT, starting_after)

        for order in stripe_response.auto_paging_iter():
            # if objects with given ID already exists - we delete it and create a new one (it was updated, so we want
            # just to replace it)
            # order = json.loads(order)
            ImportedStripeOrder.objects.filter(stripe_id=order['id'], account_id=self.id).delete()
            imported_stripe_order = ImportedStripeOrder.create_from_json(self, order)

            if max_updated_at is None or order['created'] > max_updated_at:
                max_updated_id = order['id']
                max_updated_at = order['created']

            # mapping data & sending it out
            mapped_data = self.map_data(imported_stripe_order)
            object_imported.send(sender=None, importer_account=self, mapped_data=mapped_data)

        self.last_api_items_dates['order_id'] = max_updated_id
        self.last_api_items_dates['order_created'] = max_updated_at
        self.save()

    def _call_fetch_orders(self, api_key, limit, starting_after=None):
        """
        Only broken out from _import_orders to allow for unit testing
        """
        stripe.api_key = api_key
        stripe_response = stripe.Order.list(limit=limit, starting_after=starting_after)

        return stripe_response

    def _fetch_data_inner(self):
        # TODO
        # - may be able to collapse this and _import_orders

        # Stripe's API doesn't allow to pull by date but will give you all Orders
        # before or after a given id instead
        last_updated_id = self.last_api_items_dates.get('order_id', None)
        self._import_orders(starting_after=last_updated_id)

    def __unicode__(self):
        return self.name

DataImporter.register(StripeAccount)


class ImportedStripeOrder(StorageDynamicDocument):
    account_model = StripeAccount
    prefix = "stripe"


class StripeErrorLog(AbstractErrorLog):
    account = models.ForeignKey(StripeAccount)

    @classmethod
    def map_error(cls, error):
        if '400' in error or 'Bad Request' in error:
            return "The request was unacceptable, often due to missing a required parameter."
        if '401' in error or 'Unauthorized' in error:
            return "No valid API key provided."
        if '402' in error or 'Request Failed' in error:
            return "The parameters were valid but the request failed."
        elif '404' in error or 'Not Found' in error:
            return "The requested resource doesn't exist."
        elif '409' in error or 'Conflict' in error:
            return "The request conflicts with another request (perhaps due to using the same idempotent key)."
        elif '429' in error or 'Too Many Requests' in error:
            return "Too many requests hit the API too quickly. We recommend an exponential backoff of your requests."
        elif '500' in error or '502' in error or '503' in error or '504' in error or 'Server Error' in error:
            return "Something went wrong on Stripe's end. (These are rare.)"
        else:
            return "Unrecognized"
