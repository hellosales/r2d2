# -*- coding: utf-8 -*-
from django.conf.urls import patterns, url

from r2d2.emails.views import FakeEmailSend
from django.contrib.admin.views.decorators import staff_member_required


urlpatterns = patterns('',
                       url(r"$", staff_member_required(FakeEmailSend.as_view())),
                       )
