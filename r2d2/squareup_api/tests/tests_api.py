# -*- coding: utf-8 -*-
""" tests for squareup api """
import requests_mock

from copy import copy
from rest_framework.reverse import reverse

from django.conf import settings

from r2d2.squareup_api.models import SquareupAccount
from r2d2.utils.test_utils import APIBaseTestCase


ACCOUNT_NAME = 'some name'
ACCOUNT_NAME2 = 'other name'
AUTH_RESPONSE = "http://localhost:8000/squareup/auth/callback?code=nG6OZZZ4TH-ajn82dMG3mg&response_type=code#="
TOKEN_JSON_MOCK = {'access_token': 'SVYHS6Gk2apDw8ScRLkwag', 'token_type': 'bearer', 'merchant_id': '0GDD85Z6AAFCQ',
                   'expires_at': '2016-04-03T13:06:21Z'}
RENEW_TOKEN_JSON_MOCK = {'access_token': 'Gc7t0eNwUxSDTBMQE7VMVQ', 'token_type': 'bearer',
                         'merchant_id': '0GDD85Z6AAFCQ', 'expires_at': '2016-04-03T13:08:21Z'}


class SquareupApiTestCase(APIBaseTestCase):
    """ tests for squareup API """
    def setUp(self):
        self._create_user()

    def test_setting_up_account(self):
        """ test if checking / setting up account conenction works fine """
        # get / post account info - should not work without user
        response = self.client.get(reverse('squareup-accounts'))
        self.assertEqual(response.status_code, 401)
        response = self.client.post(reverse('squareup-accounts'), {'name': ACCOUNT_NAME})
        self.assertEqual(response.status_code, 401)

        # list should be empty
        self._login()
        response = self.client.get(reverse('squareup-accounts'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data['results']), 0)

        # creating a new account
        response = self.client.post(reverse('squareup-accounts'), {'name': ACCOUNT_NAME})
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data['name'], ACCOUNT_NAME)
        self.assertFalse(response.data['is_authorized'])
        self.assertTrue(response.data['in_authorization'])
        self.assertIn('authorization_url', response.data)

        # creating second acount - and checking if 'in authorization' flag for the first account was set to false
        response = self.client.post(reverse('squareup-accounts'), {'name': ACCOUNT_NAME2})
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data['name'], ACCOUNT_NAME2)
        self.assertFalse(response.data['is_authorized'])
        self.assertTrue(response.data['in_authorization'])
        self.assertIn('authorization_url', response.data)

        response = self.client.get(reverse('squareup-accounts'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data['results']), 2)
        for result in response.data['results']:
            if result['name'] == ACCOUNT_NAME:
                self.assertFalse(result['in_authorization'])
                self.assertIsNotNone(result['authorization_url'])
            elif result['name'] == ACCOUNT_NAME2:
                self.assertTrue(result['in_authorization'])
                self.assertIsNotNone(result['authorization_url'])

        # # let's pretend we have called authorization_url and now we have the callback:
        with requests_mock.mock() as m:
            m.post('https://connect.squareup.com/oauth2/token', json=TOKEN_JSON_MOCK)
            response = self.client.get(AUTH_RESPONSE)
            self.assertEqual(response.status_code, 200)

        # check if token was updated
        response = self.client.get(reverse('squareup-accounts'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data['results']), 2)
        for result in response.data['results']:
            if result['name'] == ACCOUNT_NAME:
                self.assertFalse(result['is_authorized'])
            elif result['name'] == ACCOUNT_NAME2:
                self.assertTrue(result['is_authorized'])

        # test refreshing token
        account_query = SquareupAccount.objects.filter(access_token__isnull=False)
        self.assertEqual(account_query.count(), 1)

        account = account_query[0]
        account_to_renew = SquareupAccount.objects.get(pk=account.pk)

        with requests_mock.mock() as m:
            m.post('https://connect.squareup.com/oauth2/clients/%s/access-token/renew' % settings.SQUAREUP_API_KEY,
                   json=RENEW_TOKEN_JSON_MOCK,
                   request_headers={'Authorization': 'Client %s' % settings.SQUAREUP_API_SECRET})
            account_to_renew.refresh_token()

        self.assertNotEqual(account.access_token, account_to_renew.access_token)
        self.assertNotEqual(account.token_expiration, account_to_renew.token_expiration)

    def test_retrieve_update_delete_account(self):
        """ test plan:
            * create account with an access_token (by hand)
            * retrieve it by pk by API [authorization url should not be present]
            * remove access_token (by API) - [authorization url should be present]
            * delete account (by API) """
        self.assertEqual(SquareupAccount.objects.count(), 0)

        account = SquareupAccount.objects.create(user=self.user, name=ACCOUNT_NAME,
                                                 access_token=TOKEN_JSON_MOCK['access_token'])
        self.assertEqual(SquareupAccount.objects.count(), 1)

        # get account
        response = self.client.get(reverse('squareup-accounts', kwargs={'pk': account.pk}))
        self.assertEqual(response.status_code, 401)

        self._login()
        response = self.client.get(reverse('squareup-accounts', kwargs={'pk': account.pk}))
        self.assertEqual(response.status_code, 200)
        self.assertIsNone(response.data['authorization_url'])
        self.assertTrue(response.data['is_authorized'])

        # remove access_token - this is the way to re-authorize the account
        put_data = copy(response.data)
        put_data['access_token'] = ''
        response = self.client.put(reverse('squareup-accounts', kwargs={'pk': account.pk}), put_data)
        self.assertIsNotNone(response.data['authorization_url'])
        self.assertFalse(response.data['is_authorized'])

        # delete account
        response = self.client.delete(reverse('squareup-accounts', kwargs={'pk': account.pk}))
        self.assertEqual(response.status_code, 204)
        self.assertEqual(SquareupAccount.objects.count(), 0)
