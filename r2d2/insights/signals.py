from django.dispatch import Signal
from django.db import connection

from r2d2.insights import generators
from r2d2.insights.tasks import send_insight_task


data_fetched = Signal(providing_args=["account", "fetched_from_all", "success"])


def insight_post_save(sender, instance, created, **kwargs):
    send_notification = created
    if send_notification:
        if instance.generator_class != "Manual":
            # This is old code for looking up generator class, only used in testing
            # TODO: replace with direct BaseGenerator reference once testing code is updated
            generator_class = getattr(generators, instance.generator_class, None)
            if generator_class:
                send_notification = generator_class.EMAIL_NOTIFICATION
            else:
                send_notification = False

    if send_notification:
        # it goes through task since on the post_save we don't have attachments yet
        connection.on_commit(lambda: send_insight_task.apply_async([instance.pk], countdown=5))
