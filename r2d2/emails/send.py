# -*- coding: utf-8 -*-
import cssutils
import logging

from django.conf import settings
from django.contrib.sites.models import Site
from django.core.mail import EmailMessage
from django.template.loader import render_to_string

from premailer import Premailer

cssutils.log.setLevel(logging.CRITICAL)
logger = logging.getLogger(__name__)


def send_email(template, to, subject, variables={}, fail_silently=False, replace_variables={}, cc=None, bcc=None):

    if not isinstance(to, (list, tuple)):
        to = [to]

    logger.info(u"Sending message '%s' to recipients: %s", subject, to)

    variables['site'] = Site.objects.get_current()
    variables['STATIC_URL'] = settings.STATIC_URL
    variables['MEDIA_URL'] = settings.MEDIA_URL
    variables['is_secure'] = getattr(settings, 'IS_SECURE', False)
    html = render_to_string('emails/email_%s.html' % template, variables)
    protocol = 'https://' if variables['is_secure'] else 'http://'
    replace_variables['protocol'] = protocol
    domain = variables['site'].domain
    replace_variables['domain'] = domain

    for key, value in replace_variables.iteritems():
        if not value:
            value = ''
        html = html.replace('{%s}' % key.upper(), value)

    # Update path to have domains
    base = protocol + domain
    html = Premailer(html,
                     remove_classes=False,
                     exclude_pseudoclasses=False,
                     keep_style_tags=True,
                     include_star_selectors=True,
                     strip_important=False,
                     base_url=base).transform()
    email = EmailMessage(subject, html, settings.DEFAULT_FROM_EMAIL, to, cc=cc, bcc=bcc)
    email.content_subtype = "html"

    email.send(fail_silently=fail_silently)
