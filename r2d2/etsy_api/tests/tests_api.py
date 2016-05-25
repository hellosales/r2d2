# -*- coding: utf-8 -*-
""" tests for etsy """
import mock

from copy import copy
from oauth2 import Token
from rest_framework.reverse import reverse

from r2d2.etsy_api.models import EtsyAccount
from r2d2.utils.test_utils import APIBaseTestCase


ACCOUNT_NAME = 'some name'
AUTH_RESPONSE = ('http://localhost:8000/etsy/auth/callback?id=%d&oauth_token=ec59018efdd2a5625f305fadccb0c5'
                 '&oauth_verifier=fb82e71d#_=_')
MOCK_TOKEN = Token.from_string('oauth_token=5f5f41deb2e7e6acae9933965dd99f&oauth_token_secret=dd9967f234')

MOCKED_REQUEST_TOKEN = Token.from_string('oauth_token=a93ab1fd61b891bef654fe8ae7773b&oauth_token_secret=3189eae93c')


class EtsyApiTestCase(APIBaseTestCase):
    """ tests for Etsy API """
    def setUp(self):
        self._create_user()

    def test_setting_up_account(self):
        """ test if checking / setting up account conenction works fine """
        # get / post account info - should not work without user
        with mock.patch('etsy.oauth.EtsyOAuthClient.get_request_token') as mocked_get_request_token:
            mocked_get_request_token.return_value = MOCKED_REQUEST_TOKEN

            response = self.client.get(reverse('etsy-accounts'))
            self.assertEqual(response.status_code, 401)
            response = self.client.post(reverse('etsy-accounts'), {'name': ACCOUNT_NAME})
            self.assertEqual(response.status_code, 401)

            # list should be empty
            self._login()
            response = self.client.get(reverse('etsy-accounts'))
            self.assertEqual(response.status_code, 200)
            self.assertEqual(len(response.data['results']), 0)

            # creating a new account
            response = self.client.post(reverse('etsy-accounts'), {'name': ACCOUNT_NAME})
            self.assertEqual(response.status_code, 201)
            self.assertEqual(response.data['name'], ACCOUNT_NAME)
            self.assertFalse(response.data['is_authorized'])
            self.assertIn('authorization_url', response.data)
            account_pk = response.data['pk']
            etsy_account = EtsyAccount.objects.get(pk=account_pk)
            self.assertIsNotNone(etsy_account.request_token)

            # let's pretend we have called authorization_url and now we have the callback:
            with mock.patch('etsy.oauth.EtsyOAuthClient.get_access_token') as get_access_token:
                get_access_token.return_value = MOCK_TOKEN
                response = self.client.get(AUTH_RESPONSE % account_pk)
                self.assertEqual(response.status_code, 200)

            # check if token was updated
            response = self.client.get(reverse('etsy-accounts'))
            self.assertEqual(response.status_code, 200)
            self.assertEqual(len(response.data['results']), 1)
            self.assertTrue(response.data['results'][0]["is_authorized"])
            self.assertIsNone(response.data['results'][0]['authorization_url'])

    def test_retrieve_update_delete_account(self):
        """ test plan:
            * create account with an access_token (by hand)
            * retrieve it by pk by API [authorization url should not be present]
            * remove access_token (by API) - [authorization url should be present]
            * delete account (by API) """
        with mock.patch('etsy.oauth.EtsyOAuthClient.get_request_token') as mocked_get_request_token:
            mocked_get_request_token.return_value = MOCKED_REQUEST_TOKEN

            self.assertEqual(EtsyAccount.objects.count(), 0)

            account = EtsyAccount.objects.create(user=self.user, name=ACCOUNT_NAME, access_token=MOCK_TOKEN.to_string())
            self.assertEqual(EtsyAccount.objects.count(), 1)

            # get account
            response = self.client.get(reverse('etsy-accounts', kwargs={'pk': account.pk}))
            self.assertEqual(response.status_code, 401)

            self._login()
            response = self.client.get(reverse('etsy-accounts', kwargs={'pk': account.pk}))
            self.assertEqual(response.status_code, 200)
            self.assertIsNone(response.data['authorization_url'])
            self.assertTrue(response.data['is_authorized'])

            # remove access_token - this is the way to re-authorize the account
            put_data = copy(response.data)
            put_data['access_token'] = ''
            response = self.client.put(reverse('etsy-accounts', kwargs={'pk': account.pk}), put_data)
            self.assertIsNotNone(response.data['authorization_url'])
            self.assertFalse(response.data['is_authorized'])

            # delete account
            response = self.client.delete(reverse('etsy-accounts', kwargs={'pk': account.pk}))
            self.assertEqual(response.status_code, 204)
            self.assertEqual(EtsyAccount.objects.count(), 0)
