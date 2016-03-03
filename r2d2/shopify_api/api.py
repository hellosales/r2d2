# -*- coding: utf-8 -*-
""" (c) @ Arabel.la 2016

    shopify API

    authors: Pawel Krzyzaniak"""
from rest_framework.generics import ListCreateAPIView

from r2d2.shopify_api.models import ShopifyStore
from r2d2.shopify_api.serializers import ShopifyStoreSerializer


class ShopifyStoreAPI(ListCreateAPIView):
    """ API for creating & managing stores """
    serializer_class = ShopifyStoreSerializer
    queryset = ShopifyStore.objects.all()
    ordering = ('name',)

    def get_queryset(self):
        queryset = super(ShopifyStoreAPI, self).get_queryset()
        queryset = queryset.filter(user=self.request.user)
        return queryset

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
