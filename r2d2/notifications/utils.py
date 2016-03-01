from django.utils.translation import ugettext_lazy as _
from django.conf import settings

from r2d2.emails.send import send_email
from r2d2.utils.publisher import publish


def add_notification(user, content, subject, url, category=None, title=''):
    from .models import Notification, Category
    if category is None:
        category, created = Category.objects.get_or_create(name=settings.DEFAULT_NOTIFICATIONS_CATEGORY_NAME)
    data = {
        'user': user,
        'content': content,
        'subject': subject,
        'url': url,
        'category': category,
        'title': title,
    }
    Notification.objects.create(**data)


def send_notification(user, notification_dict=None):
    if notification_dict is None:
        notification_dict = {}
    send_email('notifications', user.email, _('Your Cadre notifications'), notification_dict)


def publish_unread_notifications(user):
    from r2d2.notifications.models import Notification
    unread = Notification.objects.filter(user=user, is_read=False).count()
    if unread:
        publish(user, None, {'has_unread_notifications': True})
    else:
        publish(user, None, {'has_unread_notifications': False})
