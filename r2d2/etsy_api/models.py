# -*- coding: utf-8 -*-
""" etsy models """
from constance import config
from datetime import datetime
from decimal import Decimal
from etsy import Etsy
from etsy.oauth import EtsyEnvProduction
from etsy.oauth import EtsyOAuthClient
from oauth2 import Token

from django.conf import settings
from django.db import models

from r2d2.common_layer.signals import object_imported
from r2d2.data_importer.api import DataImporter
from r2d2.data_importer.models import AbstractDataProvider
from r2d2.data_importer.models import AbstractErrorLog
from r2d2.utils.documents import StorageDynamicDocument


class EtsyRequestToken(models.Model):
    request_token = models.CharField(max_length=255, null=True, blank=True)
    created = models.DateTimeField(auto_now_add=True)  # TODO: drop old request tokens


class EtsyAccount(AbstractDataProvider):
    """ model for storing connection between etsy accounts and user

        this model keeps also token if the user authorized
        our app to use this account"""
    MAX_REQUEST_LIMIT = 100

    @classmethod
    def get_serializer(cls):
        from r2d2.etsy_api.serializers import EtsyAccountSerializer
        return EtsyAccountSerializer

    @classmethod
    def get_error_log_class(cls):
        return EtsyErrorLog

    @classmethod
    def get_oauth_url_serializer(cls):
        from r2d2.etsy_api.serializers import EtsyOauthUrlSerializer
        return EtsyOauthUrlSerializer

    def save(self, *args, **kwargs):
        super(EtsyAccount, self).save(*args, **kwargs)
        # it is no longer possible to save unauthorized account
        self.user.data_importer_account_authorized()

    @classmethod
    def authorization_url(cls):
        """ getting authorization url for the account & storing request token """
        client = EtsyOAuthClient(settings.ETSY_API_KEY, settings.ETSY_API_SECRET, etsy_env=EtsyEnvProduction())
        etsy_request_token = EtsyRequestToken.objects.create()

        callback_link = '%s://%s%s?id=%d' % ('https' if getattr(settings, 'IS_SECURE', False) else 'http',
                                             config.CLIENT_DOMAIN, settings.ETSY_CALLBACK_ENDPOINT,
                                             etsy_request_token.pk)

        authorization_url = client.get_signin_url(oauth_callback=callback_link)
        etsy_request_token.request_token = client.token.to_string()
        etsy_request_token.save()

        return authorization_url

    @classmethod
    def get_access_token(cls, oauth_verifier, request_id):
        """ gets access token and stores it into the model """
        try:
            etsy_request_token = EtsyRequestToken.objects.get(id=request_id)
        except EtsyRequestToken.DoesNotExist:
            return None

        client = EtsyOAuthClient(settings.ETSY_API_KEY, settings.ETSY_API_SECRET, etsy_env=EtsyEnvProduction(),
                                 token=Token.from_string(etsy_request_token.request_token))
        token = client.get_access_token(oauth_verifier)

        if not token:
            return None

        return token.to_string()

    def _prepare_api(self):
        if not self._etsy_api and self.access_token:
            client = EtsyOAuthClient(settings.ETSY_API_KEY, settings.ETSY_API_SECRET, etsy_env=EtsyEnvProduction(),
                                     token=Token.from_string(self.access_token))
            self._etsy_api = Etsy(settings.ETSY_API_KEY, etsy_env=EtsyEnvProduction, etsy_oauth_client=client)
            return True
        else:
            return False

    # etsy api methods are dynamicly created (they are queried from the server), so we can not mock them directly
    def _call_fetch_user(self, **kwargs):
        return self._etsy_api.getUser(**kwargs)

    def _call_fetch_shops(self, **kwargs):
        return self._etsy_api.findAllUserShops(**kwargs)

    def _call_fetch_transactions(self, **kwargs):
        return self._etsy_api.findAllShopTransactions(**kwargs)

    def _call_fetch_receipts(self, **kwargs):
        return self._etsy_api.findAllShopReceipts(**kwargs)

    def _fetch_user(self):
        return self._call_fetch_user(user_id='__SELF__')[0]['user_id']

    def _fetch_user_shops(self, user_id):
        shops_ids = []
        for shop in self._call_fetch_shops(user_id=user_id, limit=100):
            shops_ids.append(shop['shop_id'])
            ImportedEtsyShop.objects.filter(shop_id=shop['shop_id'], account_id=self.id).delete()
            ImportedEtsyShop.create_from_json(self, shop)
        return shops_ids

    def _fetch_transactions(self, shop_id):
        offset = ImportedEtsyTransaction.objects.filter(account_id=self.id, shop_id=shop_id).count()
        kwargs = {
            'shop_id': shop_id,
            'offset': offset,
            'limit': self.MAX_REQUEST_LIMIT
        }
        while True:
            transactions = self._call_fetch_transactions(**kwargs)
            for transaction in transactions:
                ImportedEtsyTransaction.objects.filter(transaction_id=transaction['transaction_id'],
                                                       account_id=self.id).delete()
                ImportedEtsyTransaction.create_from_json(self, transaction)

            if len(transactions) < self.MAX_REQUEST_LIMIT:
                break

            offset += self.MAX_REQUEST_LIMIT

    def _fetch_receipts(self, shop_id):
        kwargs = {
            'shop_id': shop_id,
            'offset': 0,
            'limit': self.MAX_REQUEST_LIMIT
        }
        if 'receipt' in self.last_api_items_dates:
            kwargs['min_last_modified'] = self.last_api_items_dates['receipt']

        imported_receipts = []
        while True:
            receipts = self._call_fetch_receipts(**kwargs)

            for receipt in receipts:
                ImportedEtsyReceipt.objects.filter(receipt_id=receipt['receipt_id'], account_id=self.id).delete()
                imported_receipts.append(ImportedEtsyReceipt.create_from_json(self, receipt))

                if ('receipt' not in self.last_api_items_dates or
                        self.last_api_items_dates['receipt'] < receipt['last_modified_tsz']):
                    self.last_api_items_dates['receipt'] = receipt['last_modified_tsz']
                    self.save()

            if len(receipts) < self.MAX_REQUEST_LIMIT:
                break

            kwargs['offset'] += self.MAX_REQUEST_LIMIT
        return imported_receipts

    def map_data(self, receipt, transactions):
        mapped_data = {
            'user_id': self.user_id,
            'transaction_id': str(receipt.receipt_id),
            'date': datetime.fromtimestamp(receipt.creation_tsz).isoformat(),
            'total_price': Decimal(receipt.total_price),
            'total_tax': Decimal(receipt.total_tax_cost) + Decimal(receipt.total_vat_cost),
            'total_discount': Decimal(receipt.discount_amt),
            'total_total': Decimal(receipt.adjusted_grandtotal),
            'currency_code': receipt.currency_code, # NOTE transaction and payment also list currencies but we'll just use this one at launch
            'products': []
        }

        for item in transactions:
            mapped_product = {
                'name': item.title,
                'sku': str(item.listing_id),
                'quantity': Decimal(item.quantity),
                'price': Decimal(item.price),
                'tax': None,
                'discount': None,
                'total': Decimal(item.price)
            }
            mapped_data['products'].append(mapped_product)

        return mapped_data

    def _fetch_data_inner(self):
        if not self._prepare_api():
            raise Exception('failed to set up API')

        user_id = self._fetch_user()
        shops_ids = self._fetch_user_shops(user_id)
        for shop_id in shops_ids:
            self._fetch_transactions(shop_id)
            receipts = self._fetch_receipts(shop_id)

            for receipt in receipts:
                transactions = ImportedEtsyTransaction.objects.filter(receipt_id=receipt.receipt_id)
                mapped_data = self.map_data(receipt, transactions)
                object_imported.send(sender=None, importer_account=self, mapped_data=mapped_data)

            # ## it is reduntant, but if Matt decide he wants us to import it:
            # for receipt_id in recepit_ids:
            #     # self._etsy_api.findShopPaymentByReceipt(shop_id=, receipt_id=)
            #     payment_id = self._fetch_payment(shop_id, receipt_id)
            #     self._fetch_payment_adjustment(payment_id)  # self._etsy_api.findPaymentAdjustments(payment_id=)

    def __init__(self, *args, **kwargs):
        super(EtsyAccount, self).__init__(*args, **kwargs)
        self._etsy_api = None
        self.official_channel_name = 'Etsy'

    def __unicode__(self):
        return self.name

DataImporter.register(EtsyAccount)


ETSY_PREFIX = ""  # not necessary, etsy ids are always prefixed, i.e. 'shop_id' or 'user_id', never just 'id'


class ImportedEtsyShop(StorageDynamicDocument):
    account_model = EtsyAccount
    prefix = ETSY_PREFIX


class ImportedEtsyTransaction(StorageDynamicDocument):
    account_model = EtsyAccount
    prefix = ETSY_PREFIX


class ImportedEtsyReceipt(StorageDynamicDocument):
    account_model = EtsyAccount
    prefix = ETSY_PREFIX

    @property
    def last_modified(self):
        return datetime.fromtimestamp(self.creation_tsz)

# class ImportedEtsyPayment(StorageDynamicDocument):
#     account_model = EtsyAccount
#     prefix = ETSY_PREFIX


# class ImportedEtsyPaymentAdjustment(StorageDynamicDocument):
#     account_model = EtsyAccount
#     prefix = ETSY_PREFIX


class EtsyErrorLog(AbstractErrorLog):
    account = models.ForeignKey(EtsyAccount)

    @classmethod
    def map_error(cls, error):
        if '400' in error or 'Bad Request' in error:
            return ("You've made an error in your request (such as passing a string for a parameter"
                    " that expects a number).")
        elif '403' in error or 'Forbidden' in error:
            return "You've exceeded the rate limits for your account, or the data you're trying to access is private."
        elif '404' in error or 'Not Found' in error:
            return "The requested resource could not be found, or the URI doesn't correspond to any known command."
        elif '500' in error or 'Server Error' in error:
            return ("An internal error on our side. If this problem persists, submit a bug report in the bug section"
                    " of our forums.")
        elif '503' in error or 'Service Unavailable' in error:
            return "The Etsy API is down for scheduled maintenance; please try again later (this should be rare!)"
        else:
            return "Unrecognized"
