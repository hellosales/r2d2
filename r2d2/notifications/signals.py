from .utils import send_notification


def notification_post_save(sender, instance, created, **kwargs):
    from r2d2.notifications.models import Notification
    from r2d2.notifications.utils import publish_unread_notifications

    publish_unread_notifications(instance.user)

    if not instance.is_sent:
        send_notification(instance.user, instance.as_dict())
        Notification.objects.filter(pk=instance.pk).update(is_sent=True)  # to skip post save signal
