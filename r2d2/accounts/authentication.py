from rest_framework import exceptions
from rest_framework.authentication import SessionAuthentication as BaseSessionAuthentication
from rest_framework.authentication import TokenAuthentication as BaseTokenAuthentication

# from project_template.notifications.utils import publish_unread_notifications


class TokenAuthentication(BaseTokenAuthentication):

    def authenticate_credentials(self, key):
        try:
            token = self.model.objects.get(key=key)
            # user = token.user
            # publish_unread_notifications(user)
        except self.model.DoesNotExist:
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
