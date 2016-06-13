from rest_framework import exceptions
from rest_framework.authentication import SessionAuthentication as BaseSessionAuthentication
from rest_framework.authentication import TokenAuthentication as BaseTokenAuthentication

# from project_template.notifications.utils import publish_unread_notifications


class TokenAuthentication(BaseTokenAuthentication):
    def authenticate_credentials(self, key):
        from r2d2.accounts.models import OneTimeToken  # there are some problems if it's outside
        self.model = self.get_model()
        try:
            token = self.model.objects.get(key=key)
        except self.model.DoesNotExist:
            try:
                one_time_token = OneTimeToken.objects.get(key=key)
                # it's creazy, but deleting one time token causes issues, so I am breaking all references
                token = one_time_token.user.token
                token = str(token)
                token = self.model.objects.get(key=token)
                one_time_token.delete()
            except OneTimeToken.DoesNotExist:
                raise exceptions.AuthenticationFailed('Invalid token')
        return (token.user, token)


class SessionAuthentication(BaseSessionAuthentication):
    def authenticate(self, request):
        """
        Returns a `User` if the request session currently has a logged in user.
        Otherwise returns `None`.
        """

        # Get the underlying HttpRequest object
        request = request._request
        user = getattr(request, 'user', None)

        # Unauthenticated, CSRF validation not required
        if not user or not user.is_active:
            return None

        self.enforce_csrf(request)

        # publish_unread_notifications(user)
        # CSRF passed with authenticated user
        return (user, None)
