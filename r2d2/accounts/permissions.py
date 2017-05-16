from rest_framework.permissions import IsAdminUser


class IsSuperUser(IsAdminUser):
    """
    SuperUser-level permission
    """

    def has_permission(self, request, view):
        return request.user.is_staff and request.user.is_superuser
