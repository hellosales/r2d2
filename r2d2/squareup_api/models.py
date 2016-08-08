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
from r2d2.data_importer.models import AbstractErrorLog
from r2d2.utils.documents import StorageDynamicDocument


class SquareupAccount(AbstractDataProvider):
    """ model for storing connection between squareup account and user,
        each user may be connected with many accounts """
    MAX_REQUEST_LIMIT = 200
    MIN_TIME = datetime(year=2013, month=1, day=1)

    token_expiration = models.DateTimeField(null=True, blank=True, db_index=True)
    merchant_id = models.CharField(max_length=255, null=True, blank=True)

    @classmethod
    def get_serializer(cls):
        from r2d2.squareup_api.serializers import SquareupAccountSerializer
        return SquareupAccountSerializer

    @classmethod
    def get_error_log_class(cls):
        return SquareupErrorLog

    @classmethod
    def get_oauth_url_serializer(cls):
        from r2d2.squareup_api.serializers import SquareupOauthUrlSerializer
        return SquareupOauthUrlSerializer

    def save(self, *args, **kwargs):
        super(SquareupAccount, self).save(*args, **kwargs)
        # it is no longer possible to save unauthorized account
        self.user.data_importer_account_authorized()

    @classmethod
    def authorization_url(cls):
        """ getting authorization url for the account """
        return settings.SQUAREUP_AUTHORIZATION_ENDPOINT % settings.SQUAREUP_API_KEY

    @classmethod
    def get_access_token(cls, authorization_code):
        """ obtain access_token using authorization code """
        request_data = {
            'client_id': settings.SQUAREUP_API_KEY,
            'client_secret': settings.SQUAREUP_API_SECRET,
            'code': authorization_code
        }

        response = requests.post(settings.SQUAREUP_ACCESS_TOKEN_ENDPOINT, request_data)
        if response.status_code == 200:
            data = response.json()
            if 'access_token' in data and data['access_token']:
                access_token = data['access_token']
                merchant_id = data.get('merchant_id', '')
                if 'expires_at' in data and data['expires_at']:
                    token_expiration = parse_date(data['expires_at'])
                else:
                    token_expiration = None
                return access_token, merchant_id, token_expiration
        return None, None, None

    def _save_token(self, data):
        """ save token from json data """
        if 'access_token' in data and data['access_token']:
            self.access_token = data['access_token']
            if 'expires_at' in data and data['expires_at']:
                self.token_expiration = parse_date(data['expires_at'])
            self.authorization_date = timezone.now()
            self.save()

            self.user.data_importer_account_authorized()
            return True
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
            raise Exception('%d / %s' % (response.status_code, response.json().get('type', '')))

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
        now = timezone.now()
        while True:
            end_time = start_time + timedelta(days=365)
            if end_time > now:
                end_time = now

            payments = self._call_payments_api('me', begin_time=start_time.isoformat(), end_time=end_time.isoformat(),
                                               limit=self.MAX_REQUEST_LIMIT)
            for payment in payments:
                ImportedSquareupPayment.objects.filter(squareup_id=payment['id'], account_id=self.id).delete()
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


class SquareupErrorLog(AbstractErrorLog):
    account = models.ForeignKey(SquareupAccount)

    @classmethod
    def map_error(cls, error):
        if '400' in error:
            if 'bad_request.missing_parameter' in error:
                return "A required parameter was missing from the request."
            elif 'bad_request.invalid_parameter' in error:
                return "The request included an invalid parameter."
            elif 'bad_request' in error:
                return "The request was otherwise malformed."
        if '401' in error:
            if 'service.not_authorized' in error:
                return "Your application is not authorized to make this request."
            elif 'oauth.revoked' in error:
                return "Your application's access token was revoked."
            elif 'oauth.expired' in error:
                return "Your application's access token has expired."
            elif 'unauthorized' in error:
                return "Authorization header format incorrect"
        elif '403' in error or 'Forbidden' in error:
            return ("The requesting application does not have permission to access the resource, typically"
                    " because the OAuth token's permission scope is insufficient.")
        elif '404' in error or 'Not Found' in error:
            return "The resource specified in the request wasn't found."
        elif '422' in error:
            return ("The request is well formed but has semantic errors. For example, this error occurs when you"
                    " attempt to create an item variation with the same SKU as an existing variation.")
        elif '429' in error:
            return ("The Connect API has received too many requests associated with the same access token or"
                    " application in too short a time span. Try your request again later.")
        elif '500' in error:
            return "Square encountered an unexpected error processing the request."
        elif '503' in error:
            return "The Connect API service is currently unavailable."

        return "Unrecognized"
