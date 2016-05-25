# -*- coding: utf-8 -*-
from django.conf.urls import patterns
from django.conf.urls import url

from rest_framework.routers import DefaultRouter

from r2d2.accounts.api import(
    AuthAPI, LogoutAPI, ResetPasswordAPI, ResetPasswordConfirmAPI, RegisterAPI, UserAPI, ChangePasswordAPI
)

urlpatterns = patterns(
    '',
    url(r'^auth$', AuthAPI.as_view(), name='auth_api'),
    url(r'^logout$', LogoutAPI.as_view(), name='logout_api'),
    url(r'^reset-password$', ResetPasswordAPI.as_view(), name='reset_password_api'),
    url(r'^reset-password-confirm$', ResetPasswordConfirmAPI.as_view(), name='reset_password_confirm_api'),
    url(r'^user$', UserAPI.as_view(), name="user_api"),
    url(r'^user/register$', RegisterAPI.as_view(), name="register_api"),
    url(r'^change-password/$', ChangePasswordAPI.as_view(), name="change_password_api"),
)

router = DefaultRouter()
urlpatterns += router.urls
