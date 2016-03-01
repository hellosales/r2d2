from rest_framework.authentication import SessionAuthentication


class UnsafeAdminSessionAuthentication(SessionAuthentication):

    def authenticate(self, request):
        http_request = request._request
        user = getattr(http_request, 'user', None)

        if not user or not user.is_active or not user.is_superuser:
            return None

        return (user, None)
