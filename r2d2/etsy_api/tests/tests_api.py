# -*- coding: utf-8 -*-
""" tests for etsy """
import mock

from copy import copy
from freezegun import freeze_time
from oauth2 import Token
from rest_framework.reverse import reverse

from django.utils import timezone

from r2d2.accounts.models import Account
from r2d2.etsy_api.models import EtsyAccount
from r2d2.etsy_api.models import EtsyRequestToken
from r2d2.utils.test_utils import APIBaseTestCase


ACCOUNT_NAME = 'some name'
ACCOUNT_NAME2 = 'other name'
OAUTH_VERIFIER = 'fb82e71d#_=_'
MOCK_TOKEN = Token.from_string('oauth_token=5f5f41deb2e7e6acae9933965dd99f&oauth_token_secret=dd9967f234')

MOCKED_REQUEST_TOKEN = Token.from_string('oauth_token=a93ab1fd61b891bef654fe8ae7773b&oauth_token_secret=3189eae93c')


class EtsyApiTestCase(APIBaseTestCase):
    """ tests for Etsy API """
    def setUp(self):
        self._create_user()

    def test_setting_up_account(self):
        """ test if checking / setting up account conenction works fine """
        # get / post account info - should not work without user
        response = self.client.get(reverse('etsy-accounts'))
        self.assertEqual(response.status_code, 401)
        response = self.client.post(reverse('etsy-accounts'), {'name': ACCOUNT_NAME})
        self.assertEqual(response.status_code, 401)

        # list should be empty
        self._login()
        response = self.client.get(reverse('etsy-accounts'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data['results']), 0)

        # getting oauth url
        with mock.patch('etsy.oauth.EtsyOAuthClient.get_request_token') as mocked_get_request_token:
            mocked_get_request_token.return_value = MOCKED_REQUEST_TOKEN

            response = self.client.post(reverse('data-importer-generate-oauth-url'), {'class': 'EtsyAccount'})
            self.assertEqual(response.status_code, 200)
            self.assertIsNotNone(response.data['oauth_url'])
            self.assertEqual(EtsyRequestToken.objects.count(), 1)
            self.assertEqual(EtsyRequestToken.objects.first().request_token, MOCKED_REQUEST_TOKEN.to_string())

        # creating a new account
        with mock.patch('etsy.oauth.EtsyOAuthClient.get_access_token') as get_access_token:
            get_access_token.return_value = MOCK_TOKEN

            # post account with account name, but without oauth data - should return error
            response = self.client.post(reverse('etsy-accounts'), {'name': ACCOUNT_NAME})
            self.assertEqual(response.status_code, 400)
            self.assertIn('oauth_verifier', response.data)
            self.assertIn('id', response.data)

            # post account with name and code - should pass
            data = {
                'name': ACCOUNT_NAME,
                'oauth_verifier': OAUTH_VERIFIER,
                'id': EtsyRequestToken.objects.first().pk
            }
            response = self.client.post(reverse('etsy-accounts'), data)
            self.assertEqual(response.status_code, 201)
            self.assertEqual(response.data['name'], ACCOUNT_NAME)
            account = EtsyAccount.objects.first()
            self.assertEqual(account.access_token, MOCK_TOKEN.to_string())

            # make sure account was mark as approved
            user = Account.objects.get(id=self.user.id)
            self.assertEqual(user.approval_status, Account.APPROVED)

            # post second account with the same name - should fail
            response = self.client.post(reverse('etsy-accounts'), data)
            self.assertEqual(response.status_code, 400)
            self.assertIn('name', response.data)

            # create second account - using proxy
            data['name'] = ACCOUNT_NAME2
            data['class'] = 'EtsyAccount'
            response = self.client.post(reverse('data-importer-accounts'), data)
            self.assertEqual(response.status_code, 201)
            self.assertEqual(response.data['name'], ACCOUNT_NAME2)

    def test_retrieve_update_delete_account(self):
        """ test plan:
            * create account with an access_token (by hand)
            * retrieve it by pk by API [authorization url should not be present]
            * remove access_token (by API) - [authorization url should be present]
            * delete account (by API) """
        self.assertEqual(EtsyAccount.objects.count(), 0)

        with freeze_time('2016-03-17'):
            account = EtsyAccount.objects.create(user=self.user, name=ACCOUNT_NAME,
                                                 access_token='some token',
                                                 authorization_date=timezone.now())
            self.assertEqual(EtsyAccount.objects.count(), 1)

        # get account
        response = self.client.get(reverse('etsy-accounts', kwargs={'pk': account.pk}))
        self.assertEqual(response.status_code, 401)

        self._login()
        response = self.client.get(reverse('etsy-accounts', kwargs={'pk': account.pk}))
        self.assertEqual(response.status_code, 200)

        # update name
        put_data = copy(response.data)
        put_data['name'] = ACCOUNT_NAME2
        response = self.client.put(reverse('etsy-accounts', kwargs={'pk': account.pk}), put_data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['name'], ACCOUNT_NAME2)

        # getting oauth url
        with mock.patch('etsy.oauth.EtsyOAuthClient.get_request_token') as mocked_get_request_token:
            mocked_get_request_token.return_value = MOCKED_REQUEST_TOKEN

            response = self.client.post(reverse('data-importer-generate-oauth-url'), {'class': 'EtsyAccount'})
            self.assertEqual(response.status_code, 200)
            self.assertIsNotNone(response.data['oauth_url'])
            self.assertEqual(EtsyRequestToken.objects.count(), 1)
            self.assertEqual(EtsyRequestToken.objects.first().request_token, MOCKED_REQUEST_TOKEN.to_string())

        # update access_token
        with freeze_time('2016-03-18'):
            with mock.patch('etsy.oauth.EtsyOAuthClient.get_access_token') as get_access_token:
                get_access_token.return_value = MOCK_TOKEN

                put_data['oauth_verifier'] = OAUTH_VERIFIER
                put_data['id'] = EtsyRequestToken.objects.first().pk
                response = self.client.put(reverse('etsy-accounts', kwargs={'pk': account.pk}), put_data)
                account = EtsyAccount.objects.first()
                self.assertEqual(account.access_token, MOCK_TOKEN.to_string())
                self.assertEqual(account.authorization_date.day, 18)

        # delete account
        response = self.client.delete(reverse('etsy-accounts', kwargs={'pk': account.pk}))
        self.assertEqual(response.status_code, 204)
        self.assertEqual(EtsyAccount.objects.count(), 0)
