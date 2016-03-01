# -*- coding: utf-8 -*-
from django.http import HttpResponseRedirect
from django.contrib.auth import REDIRECT_FIELD_NAME
from django.core.urlresolvers import reverse_lazy
from django.contrib.auth.views import redirect_to_login
from django.utils.six.moves.urllib.parse import urlparse
from django.conf import settings


def card_required(function):
    def wrap(request, *args, **kwargs):
        account = request.user

        path = request.build_absolute_uri()
        # urlparse chokes on lazy objects in Python 3, force to str
        # If the login url is the same scheme and net location then just
        # use the path as the "next" url.
        login_scheme, login_netloc = urlparse(settings.LOGIN_URL)[:2]
        current_scheme, current_netloc = urlparse(path)[:2]
        if ((not login_scheme or login_scheme == current_scheme) and
                (not login_netloc or login_netloc == current_netloc)):
            path = request.get_full_path()
        if not request.user.is_authenticated():
            return redirect_to_login(
                path, settings.LOGIN_URL, REDIRECT_FIELD_NAME)

        if account.cards.count():
            return function(request, *args, **kwargs)
        else:
            return HttpResponseRedirect(reverse_lazy('add_card'))

    wrap.__doc__ = function.__doc__
    wrap.__name__ = function.__name__
    return wrap
