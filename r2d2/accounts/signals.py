# -*- coding: utf-8 -*-
from constance import config
from django.conf import settings
from django.contrib.sites.models import Site
from django.core.urlresolvers import reverse

from r2d2.emails.send import send_email


def account_post_save(sender, instance, created, **kwargs):
    server_domain = Site.objects.get_current().domain
    client_domain = config.CLIENT_DOMAIN

    if created:
        # mail to newly registered user
        send_email('to_user_after_join', "%s <%s>" % (instance.get_full_name(), instance.email), 'Welcome to R2D2',
                   {'domain': client_domain})

        # send mail to admin that the user just joined the page
        subject = '%s just signed up!' % (instance.get_full_name())
        url = 'http://%s%s' % (server_domain, reverse('admin:accounts_account_change', args=(instance.pk,)))

        send_email('admin_user_registered', settings.USER_SIGNED_UP_ALERT_EMAIL, subject,
                   {'url': url, 'email': instance.email})

    if instance.is_active and not instance._old_is_active:
        subject = 'Great news! You have been approved'
        url = 'http://%s/user/sign-in' % (client_domain)
        send_email('account_activated', instance.email, subject, {'url': url})
