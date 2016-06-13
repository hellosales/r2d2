from rest_framework.reverse import reverse
from freezegun import freeze_time

# from django.utils.translation import ugettext_lazy as _
from django.core import mail
from r2d2.utils.test_utils import APIBaseTestCase
from r2d2.notifications.models import (
    Notification, Category
)


class NotificationApiTestCase(APIBaseTestCase):

    def test_api(self):
        self.second_user = self._new_user(2)
        self._create_user()
        mail.outbox = []
        category = Category.objects.create(name='test category')
        with freeze_time('2014-12-14'):
            Notification.objects.create(
                user=self.user,
                content='text',
                subject='12-14 test',
                category=category,
            )
        with freeze_time('2014-12-16'):
            Notification.objects.create(
                user=self.user,
                content='text',
                subject='12-16-test',
                category=category,
            )

        self.assertEqual(len(mail.outbox), 2)

        response = self.client.get(reverse('notifications_api'), {'user': self.second_user.pk})
        self.assertEqual(response.status_code, 401)

        self._login()
        response = self.client.get(reverse('notifications_api'), {'user': self.second_user.pk})
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data['detail'], 'You can only access your own notifications.')

        response = self.client.get(reverse('notifications_api'), {'user': self.user.pk})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data.get('count'), 2)
        self.assertEqual(len(response.data['results']), 2)
        self.assertIsNone(response.data['next'])
        self.assertIsNone(response.data['previous'])
        self.assertEqual(response.data['results'][0]['created'], 'December 16, 2014')
        self.assertEqual(response.data['results'][0]['subject'], '12-16-test')
        self.assertEqual(response.data['results'][0]['category'], 'test category')

        self.assertEqual(response.data['results'][1]['created'], 'December 14, 2014')
        self.assertEqual(response.data['results'][1]['subject'], '12-14 test')
        self.assertEqual(response.data['results'][1]['category'], 'test category')

        # get single notification
        notification = Notification.objects.first()
        self.assertFalse(notification.is_read)

        # access not owned notification
        self.login(email=self.second_user.email, password=self.password)
        response = self.client.get(reverse('notifications_api', args=[notification.pk]))
        self.assertEqual(response.status_code, 403)

        self._login()
        response = self.client.get(reverse('notifications_api', args=[notification.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['created'], 'December 16, 2014')
        self.assertEqual(response.data['subject'], '12-16-test')
        self.assertEqual(response.data['category'], 'test category')
        self.assertEqual(response.data['content'], 'text')
        self.assertIsNone(response.data['url'])

        # refresh and verify is read
        notification = Notification.objects.first()
        self.assertTrue(notification.is_read)
        self.assertEqual(len(mail.outbox), 2)
