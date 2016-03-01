# -*- coding: utf-8 -*-
from django.test import TestCase

from r2d2.accounts.models import Account
from r2d2.accounts.forms import AdminRegisterUserFullForm


class AccountsTests(TestCase):
    maxDiff = None

    def test_index(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)

    def test_register_user_in_admin_confirm_password_success(self):
        form = AdminRegisterUserFullForm(data={'password': 'passwordA2', 'password_confirm': "passwordA2"})
        self.failIf(form.is_valid())
        self.assertFalse(form.errors.get('password_confirm'))

    def test_basic(self):
        self.user = Account.objects.create(
            email='joe@doe.com',
            is_active=True)
        self.user.set_password('dumb-password')
        self.user.save()

        # Login
        response = self.client.post('/login/', {'login-username': 'joe@doe.com', 'login-password': 'dumb-password'})
        self.assertEqual(response.status_code, 302)

        # Logout
        self.client.get('/logout/')
