# -*- coding: utf-8 -*-
""" stripe API """
from rest_framework.generics import ListCreateAPIView
from rest_framework.generics import RetrieveUpdateDestroyAPIView

from r2d2.stripe_api.models import StripeAccount
from r2d2.stripe_api.serializers import StripeAccountSerializer
from r2d2.utils.rest_api_helpers import UserFilteredMixin


class StripeAccountListAPI(UserFilteredMixin, ListCreateAPIView):
    """ API for creating & managing stores """
    serializer_class = StripeAccountSerializer
    queryset = StripeAccount.objects.all()
    ordering = ('name',)


class StripeAccountAPI(UserFilteredMixin, RetrieveUpdateDestroyAPIView):
    """ API for updating & deleting stripe store """
    serializer_class = StripeAccountSerializer
    queryset = StripeAccount.objects.all()
