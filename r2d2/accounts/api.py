from constance import config
from django.contrib.auth import logout, login
from django.utils.translation import ugettext_lazy as _
from django.utils.safestring import mark_safe
from django.contrib.auth.tokens import default_token_generator
from django.contrib.sites.shortcuts import get_current_site
from django.conf import settings
from django.utils.http import urlsafe_base64_encode
from django.template import loader

from rest_framework.generics import CreateAPIView, GenericAPIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework import serializers
from rest_framework.authtoken.models import Token
from rest_framework.permissions import AllowAny

from r2d2.accounts.serializers import (
    AccountSerializer, AuthSerializer, ResetPasswordSerializer, ResetPasswordConfirmSerializer, RegisterSerializer,
    ChangePasswordSerializer
)
from r2d2.accounts.models import Account
from r2d2.utils.api import BadRequestException
from r2d2.emails.send import send_email


class AuthAPI(GenericAPIView):
    permission_classes = (AllowAny,)
    serializer_class = AuthSerializer
    authentication_classes = ()

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data['user']
            user.backend = 'django.contrib.auth.backends.ModelBackend'
            login(request, user)
            return Response(AccountSerializer(user).data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


def logout_user(request):
    try:
        Token.objects.get(user=request.user).delete()
    except Token.DoesNotExist:
        pass
    logout(request)


class LogoutAPI(GenericAPIView):
    serializer_class = serializers.Serializer

    def post(self, request):
        logout_user(request)
        return Response({})


class ResetPasswordAPI(CreateAPIView):
    """
        Request email to reset password
    """
    serializer_class = ResetPasswordSerializer
    permission_classes = (AllowAny,)
    authentication_classes = ()

    def perform_create(self, serializer):
        unknown_user_error = [mark_safe(_(
            'There is no account with that email address.'
        ))]

        email = serializer.validated_data['email'].lower()
        try:
            users = Account.objects.filter(email=email, is_active=True)
        except Account.DoesNotExist:
            raise BadRequestException({'email': unknown_user_error})
        if not users:
            raise BadRequestException({'email': unknown_user_error})
        if any((not user.has_usable_password())
               for user in users):
            raise BadRequestException({'email': unknown_user_error})

        for user in users:
            current_site = get_current_site(self.request)
            site_name = current_site.name
            domain = current_site.domain
            c = {
                'STATIC_URL': settings.STATIC_URL,
                'site': current_site,
                'email': user.email,
                'domain': domain,
                'client_domain': config.CLIENT_DOMAIN,
                'site_name': site_name,
                'uid': urlsafe_base64_encode(str(user.id)),
                'user': user,
                'token': urlsafe_base64_encode(str(default_token_generator.make_token(user))),
                'protocol': self.request.is_secure() and 'https' or 'http',
            }
            subject = loader.render_to_string('emails/resetPassword/subject.txt', c)
            subject = ''.join(subject.splitlines())
            send_email('reset_password', user.email, subject, c)


class ResetPasswordConfirmAPI(GenericAPIView):
    """
        Set new password with token from reset password
    """
    serializer_class = ResetPasswordConfirmSerializer
    permission_classes = (AllowAny,)
    authentication_classes = ()

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid(raise_exception=True):
            user = serializer.user
            user.set_password(serializer.validated_data['re_new_password'])
            user.save()
        return Response(AccountSerializer(user, context={'request': request}).data)


class ChangePasswordAPI(GenericAPIView):
    """ change password API """
    serializer_class = ChangePasswordSerializer

    def put(self, request):
        serializer = self.serializer_class(data=request.data, instance=request.user, context={'user': request.user})
        if serializer.is_valid():
            serializer.save()
            return Response(status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class RegisterAPI(CreateAPIView):
    """
        Register a new account
    """
    authentication_classes = ()
    permission_classes = (AllowAny,)
    serializer_class = RegisterSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            user.backend = 'django.contrib.auth.backends.ModelBackend'
            login(request, user)
            c = {
                'STATIC_URL': settings.STATIC_URL,
                'client_domain': config.CLIENT_DOMAIN,
                'protocol': self.request.is_secure() and 'https' or 'http',
            }
            send_email('account_created', user.email, _("Welcome to Hello Sales!"), c)
            return Response(AccountSerializer(user).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserAPI(GenericAPIView):
    """
        Get user information
    """
    serializer_class = AccountSerializer

    def get(self, request):
        response = Response(self.serializer_class(request.user, many=False, context={'request': request}).data)
        response['Cache-Control'] = 'no-cache'
        return response

    def put(self, request):
        serializer = self.serializer_class(data=request.data, instance=request.user, context={'user': request.user})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
