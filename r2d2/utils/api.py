# -*- coding: utf-8 -*-

from rest_framework.status import HTTP_400_BAD_REQUEST
from rest_framework.exceptions import APIException


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
