# -*- coding: utf-8 -*-
""" squareup views """
from rest_framework import status
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response

from r2d2.squareup_api.models import SquareupAccount


class SquareupCallbackAPI(GenericAPIView):
    """ handling oauth callback from squareup """

    @classmethod
    def get(cls, request):
        """ get the access token & save it into the model """

        authorization_code = request.GET.get('code', '')
        try:
            squareup_account = SquareupAccount.objects.get(in_authorization=True, user=request.user)
        except SquareupAccount.DoesNotExist:
            squareup_account = None

        if authorization_code and squareup_account and squareup_account.get_access_token(authorization_code):
            return Response(status=status.HTTP_200_OK)

        return Response(data={'error': SquareupAccount.OAUTH_ERROR}, status=status.HTTP_400_BAD_REQUEST)
