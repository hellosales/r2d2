# -*- coding: utf-8 -*-
import binascii
import os

from django.conf import settings
from django.contrib.auth.models import AbstractBaseUser
from django.contrib.auth.models import BaseUserManager
from django.contrib.auth.models import PermissionsMixin
from django.db import models
from django.utils.translation import ugettext_lazy as _

from rest_framework.authtoken.models import Token


AUTH_USER_MODEL = getattr(settings, 'AUTH_USER_MODEL', 'auth.User')


class OneTimeTokenQueryset(models.query.QuerySet):
    def get_or_create(self, defaults=None, **kwargs):
        obj, created = super(self.__class__, self).get_or_create(defaults, **kwargs)
        if created:
            return (obj, created)
        else:
            obj.delete()  # delete old token
            obj, created = super(self.__class__, self).get_or_create(defaults, **kwargs)
            return (obj, created)


class OneTimeToken(models.Model):
    """
    Copy of DRF auth token because model inheritance sucks
    """
    objects = OneTimeTokenQueryset.as_manager()

    key = models.CharField(_("Key"), max_length=40, primary_key=True)
    user = models.OneToOneField(AUTH_USER_MODEL, related_name='one_time_auth_token',
                                on_delete=models.CASCADE, verbose_name=_("User"))
    created = models.DateTimeField(_("Created"), auto_now_add=True)

    class Meta:
        # Work around for a bug in Django:
        # https://code.djangoproject.com/ticket/19422
        #
        # Also see corresponding ticket:
        # https://github.com/tomchristie/django-rest-framework/issues/705
        verbose_name = _("One Time Token")
        verbose_name_plural = _("One Time Tokens")
        app_label = 'accounts'

    def save(self, *args, **kwargs):
        if not self.key:
            self.key = self.generate_key()
        return super(OneTimeToken, self).save(*args, **kwargs)

    def generate_key(self):
        return binascii.hexlify(os.urandom(20)).decode()

    def __str__(self):
        return self.key


class AccountManager(BaseUserManager):
    def create_user(self, email=None, password=None, **extra_fields):
        if not email:
            raise ValueError('The given email must be set')
        email = AccountManager.normalize_email(email)
        user = self.model(email=email,
                          is_staff=False, is_active=True, is_superuser=False,
                          **extra_fields)
        user.gender = 'male'
        user.birth_year = 1000
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password, **extra_fields):
        u = self.create_user(email, password, **extra_fields)
        u.is_staff = True
        u.is_active = True
        u.is_superuser = True
        u.save(using=self._db)
        return u

    def get_by_email(self, username):
        return self.get(**{'email': username})


class Account(AbstractBaseUser, PermissionsMixin):

    def __init__(self, *args, **kwargs):
        super(Account, self).__init__(*args, **kwargs)
        self._old_is_active = self.is_active

    email = models.EmailField(_('email address'), max_length=110, unique=True)
    date_joined = models.DateTimeField(_('date joined'), auto_now_add=True)
    is_staff = models.BooleanField('staff status', default=False,
                                   help_text='Designates whether the user can log into this admin site.')
    is_active = models.BooleanField('active', default=True,
                                    help_text='Designates whether this user should be treated as '
                                              'active. Unselect this instead of deleting accounts.')
    first_name = models.CharField(_('first name'), max_length=255, blank=True)
    last_name = models.CharField(_('last name'), max_length=255, blank=True)
    merchant_name = models.CharField(max_length=255, null=True, blank=True)
    last_fetched_all = models.DateTimeField(null=True, blank=True)

    NOT_APPROVED = "not approved"
    APPROVED = "approved"
    APPROVAL_REVOKED = "approval revoked"
    APPROVAL_CHOICES = (
        (NOT_APPROVED, "Not Approved"),
        (APPROVED, "Approved"),
        (APPROVAL_REVOKED, "Approval Revoked")
    )
    approval_status = models.CharField(max_length=50, choices=APPROVAL_CHOICES, default=NOT_APPROVED)

    USERNAME_FIELD = 'email'

    objects = AccountManager()

    @property
    def token(self):
        token, created = Token.objects.get_or_create(user=self)
        return str(token)

    def get_by_natural_key(self, username):
        return self.get(**{self.model.USERNAME_FIELD: username})

    def get_full_name(self):
        full_name = '%s %s' % (self.first_name, self.last_name)
        return full_name.strip()

    def get_short_name(self):
        return self.first_name

    def get_username(self):
        return self.email

    def data_importer_account_authorized(self):
        if self.approval_status == self.NOT_APPROVED:
            self.approval_status = self.APPROVED
            self.save()

    def get_one_time_auth_token(self):
        token, created = OneTimeToken.objects.get_or_create(user=self)
        return str(token)

    def save(self, *args, **kwargs):
        # if user is deactivated, token should be removed, so the user is logged out
        if self.pk and not self.is_active:
            Token.objects.filter(user=self).delete()
        return super(Account, self).save(*args, **kwargs)

    def __unicode__(self):
        return self.email.split('@')[0]
