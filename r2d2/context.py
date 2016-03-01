# -*- coding: utf-8 -*-
from django.conf import settings
from django.contrib.sites.models import Site


def site(request):
    return {
        'settings': settings,
        'site': Site.objects.get_current(),
    }
