# -*- coding: utf-8 -*-
""" insights API """
from rest_framework.generics import ListAPIView

from r2d2.insights.models import Insight
from r2d2.insights.serializers import InsightSerializer
from r2d2.utils.rest_api_helpers import UserFilteredMixin
from r2d2.utils.pagination import CursorByIDPagination


class InsightsListAPI(UserFilteredMixin, ListAPIView):
    """ API for creating & managing etsy account """
    serializer_class = InsightSerializer
    queryset = Insight.objects.all()
    ordering = ('name',)
    pagination_class = CursorByIDPagination
