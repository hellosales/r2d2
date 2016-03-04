# -*- coding: utf-8 -*-
""" squareup API """
from rest_framework.generics import ListCreateAPIView

from r2d2.squareup_api.models import SquareupAccount
from r2d2.squareup_api.serializers import SquareupAccountSerializer


class SquareupAccountAPI(ListCreateAPIView):
    """ API for creating & managing accounts """
    serializer_class = SquareupAccountSerializer
    queryset = SquareupAccount.objects.all()
    ordering = ('name',)

    def get_queryset(self):
        queryset = super(SquareupAccountAPI, self).get_queryset()
        queryset = queryset.filter(user=self.request.user)
        return queryset

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
