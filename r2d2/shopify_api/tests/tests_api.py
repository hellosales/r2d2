# -*- coding: utf-8 -*-
""" tests for shopify """
import mock

from copy import copy
from freezegun import freeze_time
from rest_framework.reverse import reverse

from django.utils import timezone

from r2d2.accounts.models import Account
from r2d2.shopify_api.models import ShopifyStore
from r2d2.utils.test_utils import APIBaseTestCase


STORE_URL = 'arabel-la-store'
STORE_NAME = 'Arabel.la'
STORE_NAME2 = 'Arabella'
AUTH_DATA = {
    'code': 'a0d0223aaa75d7c3019e4f01e2dfadee',
    'hmac': 'f6d46746192848df6ee711199e33eb4ee8fc3d615a3d49e0e8353a8006fda72f',
    'shop': 'arabel-la-store.myshopify.com',
    'signature': '25e6b31fa09d8c0cb92410731a096b35',
    'timestamp': '1456992047'
}
ACCESS_TOKEN = '096f2fac29f779a334349aa69538c056'
TOKEN = 'some access token'


class ShopifyApiTestCase(APIBaseTestCase):
    """ tests for shopify API """
    def setUp(self):
        self._create_user()

    def test_setting_up_store(self):
        """ test if checking / setting up store conenction works fine """
        # get / post account info - should not work without user
        response = self.client.get(reverse('shopify-stores'))
        self.assertEqual(response.status_code, 401)
        response = self.client.post(reverse('shopify-stores'), {'name': STORE_NAME})
        self.assertEqual(response.status_code, 401)

        # list should be empty
        self._login()
        response = self.client.get(reverse('shopify-stores'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data['results']), 0)

        # getting oauth url
        response = self.client.post(reverse('data-importer-generate-oauth-url'), {'class': 'ShopifyStore'})
        self.assertEqual(response.status_code, 400)
        self.assertIn('shop_slug', response.data)

        response = self.client.post(reverse('data-importer-generate-oauth-url'), {'class': 'ShopifyStore',
                                                                                  'shop_slug': STORE_URL})
        self.assertEqual(response.status_code, 200)
        self.assertIsNotNone(response.data['oauth_url'])

        # creating a new account
        with mock.patch('shopify.session.Session.request_token') as request_token:
            request_token.return_value = ACCESS_TOKEN

            # post account with account name, but without code - should return error
            response = self.client.post(reverse('shopify-stores'), {'name': STORE_NAME})
            self.assertEqual(response.status_code, 400)
            self.assertIn('shop', response.data)
            self.assertIn('code', response.data)
            self.assertIn('timestamp', response.data)
            self.assertIn('hmac', response.data)

            # post account with name and code - should pass
            data = copy(AUTH_DATA)
            data['name'] = STORE_NAME

            response = self.client.post(reverse('shopify-stores'), data)
            self.assertEqual(response.status_code, 201)
            self.assertEqual(response.data['name'], STORE_NAME)
            self.assertEqual(response.data['shop_slug'], STORE_URL)
            account = ShopifyStore.objects.first()
            self.assertEqual(account.access_token, ACCESS_TOKEN)

            # make sure account was mark as approved
            user = Account.objects.get(id=self.user.id)
            self.assertEqual(user.approval_status, Account.APPROVED)

            # post second account with the same name - should fail
            response = self.client.post(reverse('shopify-stores'), data)
            self.assertEqual(response.status_code, 400)
            self.assertIn('name', response.data)

            # create second account - using proxy
            data['name'] = STORE_NAME2
            data['class'] = 'ShopifyStore'
            response = self.client.post(reverse('data-importer-accounts'), data)
            self.assertEqual(response.status_code, 201)
            self.assertEqual(response.data['name'], STORE_NAME2)

    def test_retrieve_update_delete_account(self):
        """ test plan:
            * create account with an access_token (by hand)
            * retrieve it by pk by API [authorization url should not be present]
            * remove access_token (by API) - [authorization url should be present]
            * delete account (by API) """
        self.assertEqual(ShopifyStore.objects.count(), 0)

        with freeze_time('2016-03-17'):
            account = ShopifyStore.objects.create(user=self.user, name=STORE_NAME,
                                                  access_token='some token',
                                                  authorization_date=timezone.now())
            self.assertEqual(ShopifyStore.objects.count(), 1)

        # get account
        response = self.client.get(reverse('shopify-stores', kwargs={'pk': account.pk}))
        self.assertEqual(response.status_code, 401)

        self._login()
        response = self.client.get(reverse('shopify-stores', kwargs={'pk': account.pk}))
        self.assertEqual(response.status_code, 200)

        # update name
        put_data = copy(response.data)
        put_data['name'] = STORE_NAME2
        response = self.client.put(reverse('shopify-stores', kwargs={'pk': account.pk}), put_data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['name'], STORE_NAME2)

        # update access_token
        with freeze_time('2016-03-18'):
            with mock.patch('shopify.session.Session.request_token') as request_token:
                request_token.return_value = ACCESS_TOKEN
                put_data = copy(AUTH_DATA)
                put_data['name'] = STORE_NAME
                response = self.client.put(reverse('shopify-stores', kwargs={'pk': account.pk}), put_data)
                account = ShopifyStore.objects.first()
                self.assertEqual(account.access_token, ACCESS_TOKEN)
                self.assertEqual(account.authorization_date.day, 18)

        # delete account
        response = self.client.delete(reverse('shopify-stores', kwargs={'pk': account.pk}))
        self.assertEqual(response.status_code, 204)
        self.assertEqual(ShopifyStore.objects.count(), 0)
