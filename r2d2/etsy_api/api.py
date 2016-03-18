# -*- coding: utf-8 -*-
""" etsy API """
from rest_framework.generics import ListCreateAPIView
from rest_framework.generics import RetrieveUpdateDestroyAPIView

from r2d2.etsy_api.models import EtsyAccount
from r2d2.etsy_api.serializers import EtsyAccountSerializer
from r2d2.utils.rest_api_helpers import UserFilteredMixin


class EtsyAccountListAPI(UserFilteredMixin, ListCreateAPIView):
    """ API for creating & managing stores """
    serializer_class = EtsyAccountSerializer
    queryset = EtsyAccount.objects.all()
    ordering = ('name',)


class EtsyAccountAPI(UserFilteredMixin, RetrieveUpdateDestroyAPIView):
    serializer_class = EtsyAccountSerializer
    queryset = EtsyAccount.objects.all()
