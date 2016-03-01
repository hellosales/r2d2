# -*- coding: utf-8 -*-
from django.conf.urls import patterns, url
from django.contrib.auth.views import password_reset, password_reset_done, password_reset_confirm

from r2d2.accounts.views import LogoutView, AccountAuthView
from r2d2.accounts.forms import PasswordResetForm, ValidatingSetPasswordForm


urlpatterns = patterns(
    '',
    url(r"^logout/$", LogoutView.as_view(), name="logout"),
    url(r"^login/$", AccountAuthView.as_view(), name="login"),
    url(r'^reset-password/$', password_reset,
        {'subject_template_name': 'emails/resetPassword/subject.txt',
         'email_template_name': 'emails/resetPassword/content.html',
         'template_name': 'accounts/resetPassword.html',
         'password_reset_form': PasswordResetForm}, name="password_reset"),
    url(r'^reset-password-confirm/(?P<uidb64>[0-9A-Za-z]+)-(?P<token>.+)/$',
        password_reset_confirm,
        {'template_name': 'accounts/resetPasswordConfirm.html',
         'set_password_form': ValidatingSetPasswordForm,
         'post_reset_redirect': '/login/?reset=1', 'extra_context': {'password_reset': True}},
        name="password_reset_confirm"),
    url(r'^reset-password-done/$', password_reset_done,
        {'template_name': 'accounts/resetPasswordDone.html'}, name="password_reset_done"),
)
