# -*- coding: utf-8 -*-
""" squareup API """
from rest_framework.generics import ListCreateAPIView
from rest_framework.generics import RetrieveUpdateDestroyAPIView

from r2d2.squareup_api.models import SquareupAccount
from r2d2.squareup_api.serializers import SquareupAccountSerializer
from r2d2.utils.rest_api_helpers import UserFilteredMixin


class SquareupAccountListAPI(UserFilteredMixin, ListCreateAPIView):
    """ API for creating & managing accounts """
    serializer_class = SquareupAccountSerializer
    queryset = SquareupAccount.objects.all()
    ordering = ('name',)


class SquareupAccountAPI(UserFilteredMixin, RetrieveUpdateDestroyAPIView):
    """ API for updating & deleting shopify store """
    serializer_class = SquareupAccountSerializer
    queryset = SquareupAccount.objects.all()
