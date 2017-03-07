# -*- coding: utf-8 -*-
""" tests for stripe """
import requests_mock
import urllib

from copy import copy
from freezegun import freeze_time
from rest_framework.reverse import reverse

from django.conf import settings
from django.utils import timezone

from r2d2.accounts.models import Account
from r2d2.stripe_api.models import StripeAccount
from r2d2.utils.test_utils import APIBaseTestCase


ACCOUNT_NAME = 'some name'
AUTH_CODE = "nG6OZZZ4TH-ajn82dMG3mg"
TOKEN_JSON_MOCK = {'access_token': 'SVYHS6Gk2apDw8ScRLkwag',
                   'merchant_id': '0GDD85Z6AAFCQ',
                   'refresh_token': 'SVYHS6Gk2apDw8ScRLkwag'}


class StripeApiTestCase(APIBaseTestCase):
    """ tests for stripe API """
    def setUp(self):
        self._create_user()

    def test_setting_up_store(self):
        """ test if checking / setting up store connection works fine """
        # get / post account info - should not work without user
        response = self.client.get(reverse('stripe-accounts'))
        self.assertEqual(response.status_code, 401)
        response = self.client.post(reverse('stripe-accounts'), {'name': ACCOUNT_NAME})
        self.assertEqual(response.status_code, 401)

        # list should be empty
        self._login()
        response = self.client.get(reverse('stripe-accounts'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data['results']), 0)

        # getting oauth url
        response = self.client.post(reverse('data-importer-generate-oauth-url'), {'class': 'StripeAccount'})
        self.assertEqual(response.status_code, 200)

        params = {'scope': settings.STRIPE_SCOPE,
                  'client_id': settings.STRIPE_CLIENT_ID,
                  'response_type': settings.STRIPE_RESPONSE_TYPE}
        self.assertEqual(response.data['oauth_url'],
                         settings.STRIPE_AUTHORIZATION_ENDPOINT + '?' + urllib.urlencode(params))

        # creating a new account
        with requests_mock.mock() as m:
            m.post(settings.STRIPE_ACCESS_TOKEN_ENDPOINT, json=TOKEN_JSON_MOCK)

            # post account with account name, but without code - should return error
            response = self.client.post(reverse('stripe-accounts'), {'name': ACCOUNT_NAME})
            self.assertEqual(response.status_code, 400)
            self.assertIn('code', response.data)

            # post account with name and code - should pass
            request_data = {'name': ACCOUNT_NAME,
                            'code': AUTH_CODE}

            response = self.client.post(reverse('stripe-accounts'), request_data)
            self.assertEqual(response.status_code, 201)
            self.assertEqual(response.data['name'], ACCOUNT_NAME)
            account = StripeAccount.objects.first()
            self.assertEqual(account.access_token, TOKEN_JSON_MOCK['access_token'])

            # make sure account was mark as approved
            user = Account.objects.get(id=self.user.id)
            self.assertEqual(user.approval_status, Account.APPROVED)

            # post second account with the same name - should fail
            response = self.client.post(reverse('stripe-accounts'), {'name': ACCOUNT_NAME, 'code': AUTH_CODE})
            self.assertEqual(response.status_code, 400)
            self.assertIn('name', response.data)

            # create second account - using proxy
            response = self.client.post(reverse('data-importer-accounts'), {'class': 'StripeAccount',
                                                                            'name': ACCOUNT_NAME + '2',
                                                                            'code': AUTH_CODE})
            self.assertEqual(response.status_code, 201)
            self.assertEqual(response.data['name'], ACCOUNT_NAME + '2')

    def test_retrieve_update_delete_account(self):
        """ test plan:
            * create account with an access_token (by hand)
            * retrieve it by pk by API [authorization url should not be present]
            * remove access_token (by API) - [authorization url should be present]
            * delete account (by API) """
        self.assertEqual(StripeAccount.objects.count(), 0)

        with freeze_time('2016-03-17'):
            account = StripeAccount.objects.create(user=self.user, name=ACCOUNT_NAME,
                                                   access_token='some token',
                                                   authorization_date=timezone.now())
            self.assertEqual(StripeAccount.objects.count(), 1)

        # get account
        response = self.client.get(reverse('stripe-accounts', kwargs={'pk': account.pk}))
        self.assertEqual(response.status_code, 401)

        self._login()
        response = self.client.get(reverse('stripe-accounts', kwargs={'pk': account.pk}))
        self.assertEqual(response.status_code, 200)

        # update name
        put_data = copy(response.data)
        put_data['name'] = ACCOUNT_NAME + '2'
        response = self.client.put(reverse('stripe-accounts', kwargs={'pk': account.pk}), put_data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['name'], ACCOUNT_NAME + '2')

        # update access_token
        with freeze_time('2016-03-18'):
            with requests_mock.mock() as m:
                m.post(settings.STRIPE_ACCESS_TOKEN_ENDPOINT, json=TOKEN_JSON_MOCK)
                put_data = copy(response.data)
                put_data['code'] = AUTH_CODE
                response = self.client.put(reverse('stripe-accounts', kwargs={'pk': account.pk}), put_data)
                account = StripeAccount.objects.first()
                self.assertEqual(account.access_token, TOKEN_JSON_MOCK['access_token'])
                self.assertEqual(account.authorization_date.day, 18)

        # delete account
        response = self.client.delete(reverse('stripe-accounts', kwargs={'pk': account.pk}))
        self.assertEqual(response.status_code, 204)
