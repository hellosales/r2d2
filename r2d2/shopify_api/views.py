# -*- coding: utf-8 -*-
""" shopify views """
import shopify

from django.conf import settings
from django.utils import timezone

from rest_framework import status
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response

from r2d2.shopify_api.models import ShopifyStore


class ShopifyCallbackAPI(GenericAPIView):
    """ handling oauth callback from shopify """

    @classmethod
    def get(cls, request):
        """ get the token & save it into the model """
        shop = request.GET.get('shop', '').replace('.myshopify.com', '').replace('http://', '').replace('https://', '')

        try:
            store = ShopifyStore.objects.get(name=shop, user=request.user)
        except ShopifyStore.DoesNotExist:
            return Response(data={'error': ShopifyStore.OAUTH_ERROR}, status=status.HTTP_400_BAD_REQUEST)

        params = {
            'shop': request.GET.get('shop', ''),
            'code': request.GET.get('code', ''),
            'timestamp': request.GET.get('timestamp', ''),
            'signature': request.GET.get('signature', ''),
            'hmac': request.GET.get('hmac', '')
        }
        shopify.Session.setup(api_key=settings.SHOPIFY_API_KEY, secret=settings.SHOPIFY_API_SECRET)
        session = shopify.Session(request.GET.get('shop', ''))
        try:
            token = session.request_token(params)
        except:  # shopify can throw here general exception
            return Response(data={'error': ShopifyStore.OAUTH_ERROR}, status=status.HTTP_400_BAD_REQUEST)

        store.access_token = token
        store.authorization_date = timezone.now()
        store.save()

        store.user.data_importer_account_authorized()

        return Response(status=status.HTTP_200_OK)
