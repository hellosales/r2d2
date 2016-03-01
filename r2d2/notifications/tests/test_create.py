# from rest_framework.reverse import reverse

# from django.utils.translation import ugettext_lazy as _
from django.core import mail

from r2d2.utils.test_utils import APIBaseTestCase
from r2d2.notifications.models import (
    Notification, Category
)


class NotificationsTestCase(APIBaseTestCase):

    def test_create(self):
        self._create_user()
        mail.outbox = []
        category = Category.objects.create(name='test category')
        Notification.objects.create(
            user=self.user,
            content='text',
            subject='subject',
            category=category,
        )
        self.assertEqual(len(mail.outbox), 1)
