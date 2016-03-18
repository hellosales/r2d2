# -*- coding: utf-8 -*-
""" shopify API """
from rest_framework.generics import ListCreateAPIView
from rest_framework.generics import RetrieveUpdateDestroyAPIView

from r2d2.shopify_api.models import ShopifyStore
from r2d2.shopify_api.serializers import ShopifyStoreSerializer
from r2d2.utils.rest_api_helpers import UserFilteredMixin


class ShopifyStoreListAPI(UserFilteredMixin, ListCreateAPIView):
    """ API for creating & managing stores """
    serializer_class = ShopifyStoreSerializer
    queryset = ShopifyStore.objects.all()
    ordering = ('name',)


class ShopifyStoreAPI(UserFilteredMixin, RetrieveUpdateDestroyAPIView):
    """ API for updating & deleting shopify store """
    serializer_class = ShopifyStoreSerializer
    queryset = ShopifyStore.objects.all()
