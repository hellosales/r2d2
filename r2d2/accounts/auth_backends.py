# -*- coding: utf-8 -*-
from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend


class Emailbackend(ModelBackend):
    def authenticate(self, email=None, password=None, *args, **kwargs):
        if email is None:
            if 'username' not in kwargs or kwargs['username'] is None:
                return None
            email = kwargs['username']
        email = email.lower()
        user_model = get_user_model()
        try:
            user = user_model.objects.get(email=email, is_active=True)
        except user_model.DoesNotExist:
            return None
        if user.check_password(password):
            return user
