# -*- coding: utf-8 -*-
import urlparse

from constance import config

from django.conf import settings
from django.contrib.auth import login as auth_login
from django.contrib.auth import logout as auth_logout
from django.core.urlresolvers import reverse_lazy
from django.http import HttpResponseRedirect
from django.views.generic import RedirectView
from django.views.generic import TemplateView

from r2d2.accounts.forms import AuthenticationForm


class LogoutView(RedirectView):
    url = reverse_lazy(settings.LOGOUT_REDIRECT_URLNAME)
    permanent = True

    def get(self, request, *args, **kwargs):
        auth_logout(request)
        response = super(LogoutView, self).get(request, *args, **kwargs)
        return response


class AccountAuthView(TemplateView):
    template_name = 'accounts/login.html'
    redirect_field_name = 'next'
    login_prefix = 'login'

    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated():
            return HttpResponseRedirect(reverse_lazy(settings.LOGIN_REDIRECT_URLNAME))

        response = super(AccountAuthView, self).get(request, *args, **kwargs)
        return response

    def get_context_data(self, *args, **kwargs):
        context = super(AccountAuthView, self).get_context_data(*args, **kwargs)
        redirect_to = self.request.GET.get(self.redirect_field_name, '')

        if not redirect_to:
            redirect_to = self.request.POST.get(self.redirect_field_name, '')

        context[self.redirect_field_name] = redirect_to
        context['form'] = AuthenticationForm(request=self.request, prefix=self.login_prefix)
        return context

    def check_redirect(self, context):
        redirect_to = context.get(self.redirect_field_name)
        if not redirect_to:
            return reverse_lazy(settings.LOGIN_REDIRECT_URLNAME)

        netloc = urlparse.urlparse(redirect_to)[1]
        if netloc and netloc != self.request.get_host():
            return reverse_lazy(settings.LOGIN_REDIRECT_URLNAME)

        return redirect_to

    def post(self, request, *args, **kwargs):
        context = self.get_context_data(*args, **kwargs)
        redirect_to = self.check_redirect(context)

        if request.method == "POST":
            form = AuthenticationForm(
                request=self.request,
                prefix=self.login_prefix,
                data=request.POST,
            )
            if form.is_valid():
                user = form.get_user()
                auth_login(request, user)
                if request.session.test_cookie_worked():
                    request.session.delete_test_cookie()
                response = HttpResponseRedirect(redirect_to)
                return response
            context['form'] = form

        self.request.session.set_test_cookie()
        return self.render_to_response(context)


class LoginAsView(TemplateView):
    template_name = 'login_admin.html'

    def get(self, request, *args, **kwargs):
        context = self.get_context_data(*args, **kwargs)
        protocol = 'https://' if getattr(settings, 'IS_SECURE', False) else 'http://'
        context['client_domain'] = protocol + config.CLIENT_DOMAIN
        context['user'] = request.user
        return self.render_to_response(context)
