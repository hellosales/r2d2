# -*- coding: utf-8 -*-
import json
from datetime import date

from rest_framework.reverse import reverse
from rest_framework.authtoken.models import Token

from django.core import mail
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode
from freezegun import freeze_time

from r2d2.utils.test_utils import APIBaseTestCase
from r2d2.accounts.models import (
    Account
)


class AccountApiTestCase(APIBaseTestCase):

    def test_api_auth(self):
        self._create_user()

        data = {}
        response = self.client.post(reverse('auth_api'), data)
        self.assertEqual(response.status_code, 400)

        data = {
            'email': self.user.email,
            'password': self.password
        }
        response = self.client.post(reverse('auth_api'), data)
        self.assertEqual(response.status_code, 200)

        auth = 'Token ' + response.data['token']

        response = self.client.post(reverse('logout_api'), HTTP_AUTHORIZATION=auth)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Token.objects.filter(user=self.user).count(), 0)

    def test_password_recovery(self):
        self._create_user()
        mail.outbox = []
        data = {}
        response = self.client.post(reverse('reset_password_api'), data=data)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(len(mail.outbox), 0)

        data = {
            'email': 'a@b.com',
        }
        response = self.client.post(reverse('reset_password_api'), data=data)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(len(mail.outbox), 0)

        data['email'] = self.user.email
        response = self.client.post(reverse('reset_password_api'), data=data)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(len(mail.outbox), 1)

        data = {}
        response = self.client.post(reverse('reset_password_confirm_api'), data=data)
        self.assertEqual(response.status_code, 400)
        self.assertIn('token', response.data)
        self.assertIn('new_password', response.data)
        self.assertIn('re_new_password', response.data)
        self.assertIn('user_id', response.data)

        data['user_id'] = urlsafe_base64_encode(str(self.user.id))
        data['token'] = urlsafe_base64_encode(default_token_generator.make_token(self.user))

        # not valid password
        data['new_password'] = 'foo'
        data['re_new_password'] = 'foo'
        response = self.client.post(reverse('reset_password_confirm_api'), data=data)
        self.assertEqual(response.status_code, 400)

        # not the same passwords
        data['new_password'] = 'foooooooo1'
        data['re_new_password'] = 'foooooooo2'
        response = self.client.post(reverse('reset_password_confirm_api'), data=data)
        self.assertEqual(response.status_code, 400)

        data['re_new_password'] = data['new_password']
        response = self.client.post(reverse('reset_password_confirm_api'), data=data)
        self.assertEqual(response.status_code, 200)

        user = Account.objects.get(id=self.user.id)
        self.assertTrue(user.check_password(data['new_password']))

    def test_register_api(self):
        self.assertEqual(Account.objects.count(), 0)
        self.assertEqual(len(mail.outbox), 0)

        data = {
            'first_name': 'Joe',
            'last_name': 'Doe',
            'password': '123456',
            'email': 'joe@doe.com',
        }

        with freeze_time('2016-03-17'):
            response = self.client.post(reverse('register_api'), data)
            self.assertEqual(response.status_code, 400)
            self.assertIn('merchant_name', response.data)
            self.assertIn('confirm_password', response.data)

            data['merchant_name'] = 'Joex'
            data['confirm_password'] = '12345'
            response = self.client.post(reverse('register_api'), data)
            self.assertEqual(response.status_code, 400)
            self.assertIn('confirm_password', response.data)

            data['confirm_password'] = '123456'
            response = self.client.post(reverse('register_api'), data)
            self.assertEqual(response.status_code, 201)
            response_data = json.loads(response.content)
            self.assertTrue('token' in response_data)

            accounts = Account.objects.all()
            self.assertEqual(accounts.count(), 1)
            self.assertTrue(accounts[0].is_active)
            self.assertEqual(accounts[0].approval_status, Account.NOT_APPROVED)
            self.assertFalse(accounts[0].is_staff)
            self.assertTrue(accounts[0].check_password('123456'))
            self.assertEqual(accounts[0].date_joined.date(), date(2016, 3, 17))

            self.assertEqual(len(mail.outbox), 0)

    def test_user_api(self):
        self._create_user()
        self._login()

        response = self.client.get(reverse('user_api'))
        self.assertEqual(response.status_code, 200)
        self.assertIn('first_name', response.data)
        self.assertIn('last_name', response.data)
        self.assertIn('id', response.data)
        self.assertIn('email', response.data)
        self.assertIn('merchant_name', response.data)

        data = {
            'first_name': 'First',
            'last_name': 'Last',
            'merchant_name': 'MU',
            'email': 'test@test.com'
        }
        response = self.client.put(reverse('user_api'), data=data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['first_name'], data['first_name'])
        self.assertEqual(response.data['last_name'], data['last_name'])
        self.assertEqual(response.data['email'], data['email'])
        self.assertEqual(response.data['merchant_name'], data['merchant_name'])

        response = self.client.put(reverse('user_api'), data={})
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data['first_name'][0], 'Fill in this field.')
        self.assertEqual(response.data['last_name'][0], 'Fill in this field.')
        self.assertEqual(response.data['merchant_name'][0], 'Fill in this field.')
        self.assertEqual(response.data['email'][0], ('Your user name needs to be an email address. You will receive '
                                                     'insights about your data and other information at this address.'))

        data = {
            'first_name': 'First',
            'last_name': 'Last',
            'merchant_name': 'MU',
        }
        response = self.client.put(reverse('user_api'), data=data)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data['email'][0], ('Your user name needs to be an email address. You will receive '
                                                     'insights about your data and other information at this address.'))

        data = {
            'first_name': 'First',
            'last_name': 'Last',
            'merchant_name': 'MU',
            'email': 'not an email'
        }
        response = self.client.put(reverse('user_api'), data=data)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data['email'][0], ('Your user name needs to be an email address. You will receive '
                                                     'insights about your data and other information at this address.'))

    def test_password_change(self):
        self._create_user()

        data = {}
        response = self.client.put(reverse('change_password_api'), data=data)
        self.assertEqual(response.status_code, 401)

        self._login()
        response = self.client.put(reverse('change_password_api'), data=data)
        self.assertIn('old_password', response.data)
        self.assertIn('new_password', response.data)
        self.assertIn('confirm_password', response.data)
        self.assertEqual(response.status_code, 400)

        data = {
            'old_password': '123456',
            'new_password': '123456',
            'confirm_password': '12345'
        }
        response = self.client.put(reverse('change_password_api'), data=data)
        self.assertIn('old_password', response.data)
        self.assertIn('new_password', response.data)
        self.assertIn('confirm_password', response.data)
        self.assertEqual(response.status_code, 400)

        data = {
            'old_password': 'dump-password',
            'new_password': 'd1234567',
            'confirm_password': 'd1234567'
        }
        response = self.client.put(reverse('change_password_api'), data=data)
        self.assertEqual(response.status_code, 200)
