# -*- coding: utf-8 -*-
""" tests for shopify """
import mock

from copy import copy
from rest_framework.reverse import reverse

from r2d2.shopify_api.models import ShopifyStore
from r2d2.utils.test_utils import APIBaseTestCase


STORE_NAME = 'arabel-la-store'
AUTH_RESPONSE = ("http://localhost:8000/shopify/auth/callback?code=a0d0223aaa75d7c3019e4f01e2dfadee"
                 "&hmac=f6d46746192848df6ee711199e33eb4ee8fc3d615a3d49e0e8353a8006fda72f"
                 "&shop=arabel-la-store.myshopify.com&signature=25e6b31fa09d8c0cb92410731a096b35&timestamp=1456992047")
TOKEN = 'some access token'


class ShopifyApiTestCase(APIBaseTestCase):
    """ tests for shopify API """
    def setUp(self):
        self._create_user()

    def test_setting_up_store(self):
        """ test if checking / setting up store conenction works fine """
        # get / put store info - should not work without user
        response = self.client.get(reverse('shopify-stores'))
        self.assertEqual(response.status_code, 401)
        response = self.client.post(reverse('shopify-stores'), {'name': STORE_NAME})
        self.assertEqual(response.status_code, 401)

        # list should be empty
        self._login()
        response = self.client.get(reverse('shopify-stores'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data['results']), 0)

        # creating a new store
        response = self.client.post(reverse('shopify-stores'), {'name': STORE_NAME})
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data['name'], STORE_NAME)
        self.assertFalse(response.data['is_authorized'])
        self.assertIn('authorization_url', response.data)

        # let's pretend we have called authorization_url and now we have the callback:
        with mock.patch('shopify.session.Session.request_token') as request_token:
            request_token.return_value = '096f2fac29f779a334349aa69538c056'
            response = self.client.get(AUTH_RESPONSE)
            self.assertEqual(response.status_code, 200)

        # check if token was updated
        response = self.client.get(reverse('shopify-stores'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data['results']), 1)
        self.assertTrue(response.data['results'][0]["is_authorized"])

    def test_retrieve_update_delete_account(self):
        """ test plan:
            * create account with an access_token (by hand)
            * retrieve it by pk by API [authorization url should not be present]
            * remove access_token (by API) - [authorization url should be present]
            * delete account (by API) """
        self.assertEqual(ShopifyStore.objects.count(), 0)

        account = ShopifyStore.objects.create(user=self.user, name=STORE_NAME, access_token=TOKEN)
        self.assertEqual(ShopifyStore.objects.count(), 1)

        # get account
        response = self.client.get(reverse('shopify-stores', kwargs={'pk': account.pk}))
        self.assertEqual(response.status_code, 401)

        self._login()
        response = self.client.get(reverse('shopify-stores', kwargs={'pk': account.pk}))
        self.assertEqual(response.status_code, 200)
        self.assertIsNone(response.data['authorization_url'])
        self.assertTrue(response.data['is_authorized'])

        # remove access_token - this is the way to re-authorize the account
        put_data = copy(response.data)
        put_data['access_token'] = ''
        response = self.client.put(reverse('shopify-stores', kwargs={'pk': account.pk}), put_data)
        self.assertIsNotNone(response.data['authorization_url'])
        self.assertFalse(response.data['is_authorized'])

        # delete account
        response = self.client.delete(reverse('shopify-stores', kwargs={'pk': account.pk}))
        self.assertEqual(response.status_code, 204)
        self.assertEqual(ShopifyStore.objects.count(), 0)
