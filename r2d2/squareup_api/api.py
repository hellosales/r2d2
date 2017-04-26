# -*- coding: utf-8 -*-
""" squareup API """
from datetime import datetime, timedelta

from rest_framework.generics import ListCreateAPIView
from rest_framework.generics import RetrieveUpdateDestroyAPIView
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
from rest_framework import status

from r2d2.squareup_api.models import SquareupAccount
from r2d2.squareup_api.serializers import SquareupAccountSerializer
from r2d2.utils.rest_api_helpers import UserFilteredMixin
from r2d2.accounts.permissions import IsSuperUser


class SquareupAccountListAPI(UserFilteredMixin, ListCreateAPIView):
    """ API for creating & managing accounts """
    serializer_class = SquareupAccountSerializer
    queryset = SquareupAccount.objects.all()
    ordering = ('name',)


class SquareupAccountAPI(UserFilteredMixin, RetrieveUpdateDestroyAPIView):
    """ API for updating & deleting shopify store """
    serializer_class = SquareupAccountSerializer
    queryset = SquareupAccount.objects.all()


class SquareupRefreshTokensAPI(GenericAPIView):
    permission_classes = (IsSuperUser,)

    def get(self, request):
        try:
            time_limit = datetime.now() - timedelta(days=2)
            for sa in SquareupAccount.objects.filter(access_token__isnull=False, token_expiration__gte=time_limit):
                sa.refresh_token()
        except:
            # TODO:  should I return 500 or raise?
            return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        return Response(status=status.HTTP_200_OK)
