# -*- coding: utf-8 -*-
""" handling callback from etsy """
from rest_framework import status
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response

from r2d2.etsy_api.models import EtsyAccount


class EtsyCallbackAPI(GenericAPIView):
    """ handling oauth callback from etsy """

    @classmethod
    def get(cls, request):
        """ get the access token & save it into the model """
        try:
            etsy_account = EtsyAccount.objects.get(id=request.GET.get('id', ''), user=request.user)
        except EtsyAccount.DoesNotExist:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        if not etsy_account.get_access_token(request.GET.get('oauth_verifier')):
            return Response(status=status.HTTP_400_BAD_REQUEST)

        return Response(status=status.HTTP_200_OK)
