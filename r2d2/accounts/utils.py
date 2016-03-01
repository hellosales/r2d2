# -*- coding: utf-8 -*-
from django.conf import settings
from django.core.mail import EmailMessage


def zendesk_ticket(subject, form, request, form_type='email'):
    email = form.cleaned_data['email']
    if form_type == 'email':
        message = """
            Email: %s
            IP: %s
        """ % (email, get_client_ip(request))
    elif form_type == 'contact':
        message = """
            Email: %s
            Subject: %s
            Message: %s
            IP: %s
        """ % (email, form.cleaned_data['subject'], form.cleaned_data['message'], get_client_ip(request))
        if request.user.is_authenticated():
            message += """
            Logged in user:
            Name: %s %s
            Email: %s
            """ % (request.user, request.user.last_name, request.user.email)
            email = request.user.email
    else:
        raise NotImplemented
    email = EmailMessage(subject, message, settings.DEFAULT_FROM_EMAIL, [settings.SUPPORT_EMAIL],
                         headers={'Reply-To': email})
    email.send()


def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip
