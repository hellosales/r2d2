# -*- coding: utf-8 -*-
""" tests for etsy """
import mock

from oauth2 import Token
from rest_framework.reverse import reverse

from r2d2.utils.test_utils import APIBaseTestCase


ACCOUNT_NAME = 'some name'
AUTH_RESPONSE = 'http://localhost:8000/etsy/auth/callback?id=1&oauth_token=ec59018efdd2a5625f305fadccb0c5&oauth_verifier=fb82e71d#_=_'
MOCK_TOKEN = Token.from_string('oauth_token=5f5f41deb2e7e6acae9933965dd99f&oauth_token_secret=dd9967f234')


class EtsyApiTestCase(APIBaseTestCase):
    """ tests for Etsy API """

    def test_setting_up_account(self):
        """ test if checking / setting up account conenction works fine """
        # get / post account info - should not work without user
        response = self.client.get(reverse('etsy-account'))
        self.assertEqual(response.status_code, 401)
        response = self.client.post(reverse('etsy-account'), {'name': ACCOUNT_NAME})
        self.assertEqual(response.status_code, 401)

        # list should be empty
        self._create_user()
        self._login()
        response = self.client.get(reverse('etsy-account'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data['results']), 0)

        # creating a new account
        response = self.client.post(reverse('etsy-account'), {'name': ACCOUNT_NAME})
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data['name'], ACCOUNT_NAME)
        self.assertFalse(response.data['is_authorized'])
        self.assertIn('authorization_url', response.data)

        # let's pretend we have called authorization_url and now we have the callback:
        with mock.patch('etsy.oauth.EtsyOAuthClient.get_access_token') as get_access_token:
            get_access_token.return_value = MOCK_TOKEN
            response = self.client.get(AUTH_RESPONSE)
            self.assertEqual(response.status_code, 200)

        # check if token was updated
        response = self.client.get(reverse('etsy-account'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data['results']), 1)
        self.assertTrue(response.data['results'][0]["is_authorized"])
        self.assertIsNone(response.data['results'][0]['authorization_url'])
