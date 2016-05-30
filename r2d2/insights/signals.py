from constance import config

from django.dispatch import Signal

from r2d2.emails.send import send_email
from r2d2.insights import generators


data_fetched = Signal(providing_args=["account", "fetched_from_all", "success"])


def insight_post_save(sender, instance, created, **kwargs):
    send_notification = True
    if instance.generator_class != "Manual":
        generator_class = getattr(generators, instance.generator_class, None)
        if generator_class:
            send_notification = generator_class.EMAIL_NOTIFICATION
        else:
            send_notification = False

    if send_notification:
        client_domain = config.CLIENT_DOMAIN

        send_email('new_insight', "%s <%s>" % (instance.user.get_full_name(), instance.user.email), 'New Insight!',
                   {'domain': client_domain, 'insight': instance})
