from django.dispatch import Signal

from r2d2.insights import generators


data_fetched = Signal(providing_args=["account", "fetched_from_all", "success"])


def insight_post_save(sender, instance, created, **kwargs):
    send_email = True
    if instance.generator_class != "Manual":
        generator_class = getattr(generators, instance.generator_class, None)
        if generator_class:
            send_email = generator_class.EMAIL_NOTIFICATION
        else:
            send_email = False

    if send_email:
        pass  # TODO
