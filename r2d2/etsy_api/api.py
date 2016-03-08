# -*- coding: utf-8 -*-
""" etsy API """
from rest_framework.generics import ListCreateAPIView

from r2d2.etsy_api.models import EtsyAccount
from r2d2.etsy_api.serializers import EtsyAccountSerializer


class EtsyAccountListAPI(ListCreateAPIView):
    """ API for creating & managing stores """
    serializer_class = EtsyAccountSerializer
    queryset = EtsyAccount.objects.all()
    ordering = ('name',)

    def get_queryset(self):
        queryset = super(EtsyAccountListAPI, self).get_queryset()
        queryset = queryset.filter(user=self.request.user)
        return queryset

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
