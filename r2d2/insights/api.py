# -*- coding: utf-8 -*-
""" insights API """
from rest_framework.generics import GenericAPIView
from rest_framework.generics import ListAPIView
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.response import Response

from r2d2.insights.models import Insight
from r2d2.insights.serializers import HeaderDataSerializer
from r2d2.insights.serializers import InsightSerializer
from r2d2.utils.rest_api_helpers import UserFilteredMixin


class InsightsListAPI(UserFilteredMixin, ListAPIView):
    """ API for creating & managing etsy account """
    serializer_class = InsightSerializer
    queryset = Insight.objects.order_by('-id').all()
    ordering = ('name',)
    pagination_class = LimitOffsetPagination


class HeaderDataApi(GenericAPIView):
    """ API for getting header information (# of insights, channels & transactions) """
    serializer_class = HeaderDataSerializer

    def get(self, request):
        return Response(self.serializer_class(request.user).data)
