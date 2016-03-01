# -*- coding: utf-8 -*-
from django.conf.urls import patterns, url

from rest_framework.routers import DefaultRouter

from r2d2.accounts.api import(
    AuthAPI, LogoutAPI, ResetPasswordAPI, ResetPasswordConfirmAPI
)

urlpatterns = patterns(
    '',
    url(r'^auth$', AuthAPI.as_view(), name='auth_api'),
    url(r'^logout$', LogoutAPI.as_view(), name='logout_api'),
    url(r'^reset-password$', ResetPasswordAPI.as_view(), name='reset_password_api'),
    url(r'^reset-password-confirm$', ResetPasswordConfirmAPI.as_view(), name='reset_password_confirm_api'),
)

router = DefaultRouter()
urlpatterns += router.urls
