# -*- coding: utf-8 -*-
from django.core.urlresolvers import reverse

from r2d2.accounts.models import OneTimeToken
from r2d2.utils.test_utils import APIBaseTestCase

from rest_framework.authtoken.models import Token


class OneTimeTokenTest(APIBaseTestCase):
    def test_log_in(self):
        self.assertEqual(OneTimeToken.objects.count(), 0)
        self.assertEqual(Token.objects.count(), 0)

        self._create_user()
        self.assertEqual(Token.objects.count(), 0)
        one_time_token = self.user.get_one_time_auth_token()

        self.assertEqual(OneTimeToken.objects.count(), 1)
        self.assertEqual(Token.objects.count(), 0)

        self.client.login(email=self.user.email, password=self.password)
        self.assertEqual(OneTimeToken.objects.count(), 1)

        # properly logged in can retrieve answer
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + one_time_token)
        response = self.client.get(reverse('user_api'))
        self.assertEqual(response.status_code, 200)

        self.assertEqual(OneTimeToken.objects.count(), 0)
        self.assertEqual(Token.objects.count(), 1)

        # tries again - fail
        response = self.client.get(reverse('user_api'))
        self.assertEqual(response.status_code, 401)

        # check with proper new token
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + str(Token.objects.first()))
        response = self.client.get(reverse('user_api'))
        self.assertEqual(response.status_code, 200)
