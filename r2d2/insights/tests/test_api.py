# -*- coding: utf-8 -*-
""" tests for insights api """
from rest_framework.reverse import reverse

from r2d2.utils.test_utils import APIBaseTestCase
from r2d2.insights.models import Insight


class InsightsAPITestCase(APIBaseTestCase):
    """ tests for Insights API """
    def setUp(self):
        user = self._create_user()
        for i in range(0, 30):
            insight = Insight.objects.create(user=user, text="insight %d" % i, generator_class="FakeGenerator")

    def test_getting_insights(self):
        """ Insights shoulde be returned in two pages [page_size = 20 elements], there shoulde be
            paginator without counts used. Insights should be returned from the newest to the oldest """

        response = self.client.get(reverse('insights'))
        self.assertEqual(response.status_code, 401)

        self._login()
        response = self.client.get(reverse('insights'))
        self.assertEqual(response.status_code, 200)
        self.assertNotIn('count', response.data)
        self.assertIsNotNone(response.data['next'])
        self.assertEqual(len(response.data['results']), 20)
        self.assertEqual(response.data['results'][0]['text'], 'insight 29')
        self.assertEqual(response.data['results'][19]['text'], 'insight 10')

        response = self.client.get(response.data['next'])
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data['results']), 10)
        self.assertEqual(response.data['results'][0]['text'], 'insight 9')
        self.assertEqual(response.data['results'][9]['text'], 'insight 0')
