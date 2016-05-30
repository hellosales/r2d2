# -*- coding: utf-8 -*-
""" tests for suggestions API """
from r2d2.utils.test_utils import APIBaseTestCase
from rest_framework.reverse import reverse


class SourceSuggestionAPITests(APIBaseTestCase):
    """ tests for suggestions API """
    def setUp(self):
        self._create_user()

    def test_api(self):
        response = self.client.post(reverse('source-suggestions-api'), {"text": "something"})
        self.assertEqual(response.status_code, 401)

        self._login()
        response = self.client.post(reverse('source-suggestions-api'), {"text": "something"})
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data['text'], 'something')
