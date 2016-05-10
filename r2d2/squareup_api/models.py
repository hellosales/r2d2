# -*- coding: utf-8 -*-
""" etsy models """
import requests

from datetime import datetime
from datetime import timedelta

from dateutil.parser import parse as parse_date
from decimal import Decimal
from django.conf import settings
from django.db import models
from django.utils import timezone

from r2d2.common_layer.signals import object_imported
from r2d2.data_importer.api import DataImporter
from r2d2.data_importer.models import AbstractDataProvider
from r2d2.utils.documents import StorageDynamicDocument


class SquareupAccount(AbstractDataProvider):
    """ model for storing connection between squareup account and user,
        each user may be connected with many accounts,

        Since squareup does not allow custom callback & there is no other identification
        of the request, we need to mark model that is in authroization, so we can retrive it
        on callback. This is the reason for 'in_authrization' flag. Setting this flag unsettle
        it for any other SquareupAccount for given user.

        Trying to authorize two account simultaneously for one user will end up a mess.

        This model keeps also token if the user authorized our app to use this account"""
    MAX_REQUEST_LIMIT = 200
    MIN_TIME = datetime(year=2013, month=1, day=1)

    in_authorization = models.BooleanField(default=True)  # on creation we assume authroization
    token_expiration = models.DateTimeField(null=True, blank=True, db_index=True)
    merchant_id = models.CharField(max_length=255, null=True, blank=True)

    @classmethod
    def get_serializer(cls):
        from r2d2.squareup_api.serializers import SquareupAccountSerializer
        return SquareupAccountSerializer

    def save(self, *args, **kwargs):
        super(SquareupAccount, self).save(*args, **kwargs)
        if self.in_authorization:
            SquareupAccount.objects.filter(user=self.user).exclude(pk=self.pk).update(in_authorization=False)

    @property
    def authorization_url(self):
        """ getting authorization url for the account """
        if self.is_authorized:
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

    def _call_payments_api(self, location, **kwargs):
        response = requests.get(settings.SQUAREUP_BASE_URL + 'v1/%s/payments' % location, params=kwargs,
                                headers={'Authorization': 'Bearer %s' % self.access_token})
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception('call returned status code %d' % response.status_code)

    def map_data(self, imported_squareup_payment):
        mapped_data = {
            'user_id': self.user_id,
            'transaction_id': imported_squareup_payment.squareup_id,
            'date': imported_squareup_payment.created_at,
            'total_price': Decimal(imported_squareup_payment.net_sales_money['amount']),
            'total_tax': Decimal(imported_squareup_payment.tax_money['amount']),
            'total_discount': Decimal(imported_squareup_payment.discount_money['amount']),
            'total_total': 0,
            'products': []
        }
        mapped_data['total_total'] = (mapped_data['total_price'] + mapped_data['total_tax'] -
                                      mapped_data['total_discount'])

        for item in imported_squareup_payment.itemizations:
            mapped_product = {
                'name': item['name'],
                'sku': item['item_detail']['sku'],
                'quantity': Decimal(item['quantity']),
                'price': Decimal(item['gross_sales_money']['amount']),
                'tax': Decimal(0),
                'discount': Decimal(item['discount_money']['amount']),
                'total': Decimal(item['total_money']['amount'])
            }
            for tax in item['taxes']:
                mapped_product['tax'] += Decimal(tax['applied_money']['amount'])
            mapped_data['products'].append(mapped_product)

        return mapped_data

    def _fetch_data_inner(self):
        start_time = self.MIN_TIME
        now = datetime.now()
        while True:
            end_time = start_time + timedelta(days=365)
            if end_time > now:
                end_time = now

            payments = self._call_payments_api('me', begin_time=start_time.isoformat(), end_time=end_time.isoformat(),
                                               limit=self.MAX_REQUEST_LIMIT)
            for payment in payments:
                ImportedSquareupPayment.objects.filter(squareup_id=payment['id']).delete()
                imported_squareup_payment = ImportedSquareupPayment.create_from_json(self, payment)

                # mapping data & sending it out
                mapped_data = self.map_data(imported_squareup_payment)
                object_imported.send(sender=None, importer_account=self, mapped_data=mapped_data)

            if len(payments) == self.MAX_REQUEST_LIMIT:
                start_time = parse_date(payments[-1]['created_at'])
            elif end_time < now:
                start_time = end_time
            else:
                break

    def __unicode__(self):
        return self.name


DataImporter.register(SquareupAccount)


class ImportedSquareupPayment(StorageDynamicDocument):
    account_model = SquareupAccount
    prefix = "squareup"
