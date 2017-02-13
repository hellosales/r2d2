# -*- coding: utf-8 -*-
""" tests for squareup api """
import requests_mock

from copy import copy
from freezegun import freeze_time
from rest_framework.reverse import reverse

from django.conf import settings
from django.utils import timezone

from r2d2.accounts.models import Account
from r2d2.squareup_api.models import SquareupAccount
from r2d2.utils.test_utils import APIBaseTestCase


ACCOUNT_NAME = 'some name'
ACCOUNT_NAME2 = 'other name'
AUTH_CODE = "nG6OZZZ4TH-ajn82dMG3mg"
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

        # getting oauth url
        response = self.client.post(reverse('data-importer-generate-oauth-url'), {'class': 'SquareupAccount'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['oauth_url'],
                         settings.SQUAREUP_AUTHORIZATION_ENDPOINT % {'client_id': settings.SQUAREUP_API_KEY,
                                                                     'scope': settings.SQUAREUP_SCOPE})

        # creating a new account
        with requests_mock.mock() as m:
            m.post('https://connect.squareup.com/oauth2/token', json=TOKEN_JSON_MOCK)

            # post account with account name, but without code - should return error
            response = self.client.post(reverse('squareup-accounts'), {'name': ACCOUNT_NAME})
            self.assertEqual(response.status_code, 400)
            self.assertIn('code', response.data)

            # post account with name and code - should pass
            response = self.client.post(reverse('squareup-accounts'), {'name': ACCOUNT_NAME, 'code': AUTH_CODE})
            self.assertEqual(response.status_code, 201)
            self.assertEqual(response.data['name'], ACCOUNT_NAME)
            account = SquareupAccount.objects.first()
            self.assertEqual(account.access_token, TOKEN_JSON_MOCK['access_token'])

            # make sure account was mark as approved
            user = Account.objects.get(id=self.user.id)
            self.assertEqual(user.approval_status, Account.APPROVED)

            # post second account with the same name - should fail
            response = self.client.post(reverse('squareup-accounts'), {'name': ACCOUNT_NAME, 'code': AUTH_CODE})
            self.assertEqual(response.status_code, 400)
            self.assertIn('name', response.data)

            # create second account - using proxy
            response = self.client.post(reverse('data-importer-accounts'), {'class': 'SquareupAccount',
                                                                            'name': ACCOUNT_NAME2,
                                                                            'code': AUTH_CODE})
            self.assertEqual(response.status_code, 201)
            self.assertEqual(response.data['name'], ACCOUNT_NAME2)

        # test refreshing token
        account_query = SquareupAccount.objects.filter(access_token__isnull=False)
        self.assertEqual(account_query.count(), 2)

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

        with freeze_time('2016-03-17'):
            account = SquareupAccount.objects.create(user=self.user, name=ACCOUNT_NAME,
                                                     access_token='some token',
                                                     authorization_date=timezone.now())
            self.assertEqual(SquareupAccount.objects.count(), 1)

        # get account
        response = self.client.get(reverse('squareup-accounts', kwargs={'pk': account.pk}))
        self.assertEqual(response.status_code, 401)

        self._login()
        response = self.client.get(reverse('squareup-accounts', kwargs={'pk': account.pk}))
        self.assertEqual(response.status_code, 200)

        # update name
        put_data = copy(response.data)
        put_data['name'] = ACCOUNT_NAME2
        response = self.client.put(reverse('squareup-accounts', kwargs={'pk': account.pk}), put_data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['name'], ACCOUNT_NAME2)

        # update access_token
        with freeze_time('2016-03-18'):
            with requests_mock.mock() as m:
                m.post('https://connect.squareup.com/oauth2/token', json=TOKEN_JSON_MOCK)
                put_data = copy(response.data)
                put_data['code'] = AUTH_CODE
                response = self.client.put(reverse('squareup-accounts', kwargs={'pk': account.pk}), put_data)
                account = SquareupAccount.objects.first()
                self.assertEqual(account.access_token, TOKEN_JSON_MOCK['access_token'])
                self.assertEqual(account.authorization_date.day, 18)

        # delete account
        response = self.client.delete(reverse('squareup-accounts', kwargs={'pk': account.pk}))
        self.assertEqual(response.status_code, 204)
        self.assertEqual(SquareupAccount.objects.count(), 0)
