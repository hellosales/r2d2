# -*- coding: utf-8 -*-
""" insights API """
import urllib2

from django.http import HttpResponse
from rest_framework import status
from rest_framework.generics import GenericAPIView
from rest_framework.generics import ListAPIView
from rest_framework.response import Response

from r2d2.insights.models import Insight
from r2d2.insights.models import InsightAttachment
from r2d2.insights.serializers import HeaderDataSerializer
from r2d2.insights.serializers import InsightSerializer
from r2d2.utils.pagination import BetterLimitOffsetPagination
from r2d2.utils.rest_api_helpers import UserFilteredMixin


class InsightsListAPI(UserFilteredMixin, ListAPIView):
    """ API for creating & managing etsy account
        limit -- limit
        offset -- offset"""
    serializer_class = InsightSerializer
    queryset = Insight.objects.order_by('-id').all()
    ordering = ('name',)
    pagination_class = BetterLimitOffsetPagination


class HeaderDataApi(GenericAPIView):
    """ API for getting header information (# of insights, channels & transactions) """
    serializer_class = HeaderDataSerializer

    def get(self, request):
        return Response(self.serializer_class(request.user).data)


class DownloadAttachmentApi(GenericAPIView):
    """ API for getting insights attachments """
    serializer_class = HeaderDataSerializer

    def get(self, request, pk):
        try:
            attachment = InsightAttachment.objects.get(insight__user=request.user, pk=pk)
            opener = urllib2.urlopen(attachment.file.url)
            response = HttpResponse(opener.read(), content_type=attachment.content_type)
            response["Content-Disposition"] = "attachment; filename=%s" % attachment.file_name
            return response
        except InsightAttachment.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
