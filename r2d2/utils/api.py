# -*- coding: utf-8 -*-

from rest_framework.status import HTTP_400_BAD_REQUEST
from rest_framework.exceptions import APIException
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
from rest_framework import status

import djmoney_rates.management.commands.update_rates as update_rates
import django.contrib.sessions.management.commands.clearsessions as clearsessions

from r2d2.accounts.permissions import IsSuperUser


class BadRequestException(APIException):
    default_detail = 'Bad request'

    def __init__(self, detail=None, status_code=HTTP_400_BAD_REQUEST):
        self.detail = detail or self.default_detail
        self.data = detail
        self.status_code = status_code


class ApiVersionMixin(object):
    """
        Use this as first in inheritance chain when creating own API classes
        Returns serializer depending on versioning_serializer_classess and version

        versioning_serializer_classess = {
            1: 'x',
            2: 'x',
        }
    """

    def get_serializer_class(self):
        if hasattr(self, 'versioning_serializer_classess') and hasattr(self.request, 'version')\
                and self.request.version is not None:
            return self.versioning_serializer_classess[int(self.request.version)]
        else:
            return self.serializer_class


class DjMoneyUpdateRatesAPI(GenericAPIView):
    permission_classes = (IsSuperUser,)

    def get(self, request):
        try:
            command = update_rates.Command()
            command.handle('yesterday')
        except:
            # TODO:  should I return 500 or raise?
            return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        return Response(status=status.HTTP_200_OK)


class DjangoClearSessionsAPI(GenericAPIView):
    permission_classes = (IsSuperUser,)

    def get(self, request):
        try:
            command = clearsessions.Command()
            command.handle()
        except:
            # TODO:  should I return 500 or raise?
            return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        return Response(status=status.HTTP_200_OK)
