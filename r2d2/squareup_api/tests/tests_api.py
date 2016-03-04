# -*- coding: utf-8 -*-
""" tests for squareup api """
import mock
import requests_mock

from rest_framework.reverse import reverse

from r2d2.utils.test_utils import APIBaseTestCase


ACCOUNT_NAME = 'some name'
ACCOUNT_NAME2 = 'other name'
AUTH_RESPONSE = "http://localhost:8000/squareup/auth/callback?code=nG6OZZZ4TH-ajn82dMG3mg&response_type=code#="
TOKEN_JSON_MOCK = {'access_token': 'SVYHS6Gk2apDw8ScRLkwag'}


class SquareupApiTestCase(APIBaseTestCase):
    """ tests for squareup API """

    def test_setting_up_account(self):
        """ test if checking / setting up account conenction works fine """
        # get / post account info - should not work without user
        response = self.client.get(reverse('squareup-account'))
        self.assertEqual(response.status_code, 401)
        response = self.client.post(reverse('squareup-account'), {'name': ACCOUNT_NAME})
        self.assertEqual(response.status_code, 401)

        # list should be empty
        self._create_user()
        self._login()
        response = self.client.get(reverse('squareup-account'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data['results']), 0)

        # creating a new account
        response = self.client.post(reverse('squareup-account'), {'name': ACCOUNT_NAME})
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data['name'], ACCOUNT_NAME)
        self.assertFalse(response.data['is_authorized'])
        self.assertTrue(response.data['in_authorization'])
        self.assertIn('authorization_url', response.data)

        # creating second acount - and checking if 'in authorization' flag for the first account was set to false
        response = self.client.post(reverse('squareup-account'), {'name': ACCOUNT_NAME2})
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data['name'], ACCOUNT_NAME2)
        self.assertFalse(response.data['is_authorized'])
        self.assertTrue(response.data['in_authorization'])
        self.assertIn('authorization_url', response.data)

        response = self.client.get(reverse('squareup-account'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data['results']), 2)
        for result in response.data['results']:
            if result['name'] == ACCOUNT_NAME:
                self.assertFalse(result['in_authorization'])
                self.assertIsNone(result['authorization_url'])
            elif result['name'] == ACCOUNT_NAME2:
                self.assertTrue(result['in_authorization'])
                self.assertIsNotNone(result['authorization_url'])

        # # let's pretend we have called authorization_url and now we have the callback:
        with requests_mock.mock() as m:
            m.post('https://connect.squareup.com/oauth2/token', json=TOKEN_JSON_MOCK)
            response = self.client.get(AUTH_RESPONSE)
            self.assertEqual(response.status_code, 200)

        # check if token was updated
        response = self.client.get(reverse('squareup-account'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data['results']), 2)
        for result in response.data['results']:
            if result['name'] == ACCOUNT_NAME:
                self.assertFalse(result['is_authorized'])
            elif result['name'] == ACCOUNT_NAME2:
                self.assertTrue(result['is_authorized'])

