# -*- coding: utf-8 -*-
from django.contrib.auth.models import AbstractBaseUser
from django.contrib.auth.models import BaseUserManager
from django.contrib.auth.models import PermissionsMixin
from django.db import models
from django.db.models.signals import post_save
from django.utils.translation import ugettext_lazy as _

from rest_framework.authtoken.models import Token

from r2d2.accounts.signals import account_post_save


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
    is_active = models.BooleanField('active', default=False,
                                    help_text='Designates whether this user should be treated as '
                                              'active. Unselect this instead of deleting accounts.')
    first_name = models.CharField(_('first name'), max_length=255, blank=True)
    last_name = models.CharField(_('last name'), max_length=255, blank=True)
    merchant_name = models.CharField(max_length=255, null=True, blank=True)

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

    def __unicode__(self):
        return self.email.split('@')[0]


post_save.connect(account_post_save, sender=Account)
