from collections import OrderedDict

from django.utils.translation import ugettext_lazy as _

from rest_framework import status
from rest_framework.exceptions import APIException
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.pagination import replace_query_param
from rest_framework.response import Response


class IncorrectLimitOffsetError(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = _('Malformed request.')


class BetterLimitOffsetPagination(LimitOffsetPagination):
    """
    A limit/offset based style. For example:

    http://api.example.org/accounts/?limit=100
    http://api.example.org/accounts/?offset=400&limit=100

    Improvements:
        - no count,
        - works

    Warning:
        - html is not handled
    """
    def paginate_queryset(self, queryset, request, view=None):
        self.limit = self.get_limit(request)
        if self.limit is None:
            raise IncorrectLimitOffsetError

        self.offset = self.get_offset(request)
        if self.offset < 0:
            self.limit += self.offset  # + because offset is negative
            self.offset = 0
        if self.limit <= 0:
            raise IncorrectLimitOffsetError

        self.request = request
        self.results = list(queryset[self.offset:self.offset + self.limit])
        return self.results

    def get_paginated_response(self, data):
        return Response(OrderedDict([
            ('next', self.get_next_link()),
            ('previous', self.get_previous_link()),
            ('results', data)
        ]))
        return self.default_limit

    def get_offset(self, request):
        try:
            return int(request.query_params[self.offset_query_param])
        except (KeyError, ValueError):
            return 0

    def get_next_link(self):
        if len(self.results) < self.limit:
            return None

        url = self.request.build_absolute_uri()
        url = replace_query_param(url, self.limit_query_param, self.limit)

        offset = self.offset + self.limit
        return replace_query_param(url, self.offset_query_param, offset)
