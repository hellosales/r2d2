# -*- coding: utf-8 -*-
from constance import config
from django.conf import settings
from django.contrib.sites.models import Site
from django.core.mail import EmailMessage
from django.core.urlresolvers import reverse

from r2d2.emails.send import send_email


def account_post_save(sender, instance, created, **kwargs):
    if created:
        # mail to newly registered user
        client_domain = config.CLIENT_DOMAIN
        send_email('to_user_after_join', "%s <%s>" % (instance.get_full_name(), instance.email), 'Welcome to R2D2',
                   {'domain': client_domain})

        # send mail to admin that the user just joined the page
        server_domain = Site.objects.get_current().domain
        subject = '%s just signed up!' % (instance.get_full_name())
        url = 'http://%s%s' % (server_domain, reverse('admin:accounts_account_change', args=(instance.pk,)))
        txt = '%s\r\n%s' % (subject, url)
        email = EmailMessage(subject, txt, settings.DEFAULT_FROM_EMAIL, settings.USER_SIGNED_UP_ALERT_EMAIL)
        email.send(fail_silently=False)
