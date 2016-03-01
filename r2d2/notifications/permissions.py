from rest_framework.permissions import IsAuthenticated


class HisOwnNotification(IsAuthenticated):
    """
    Object-level permission to only allow user to see his notification
    """

    def has_object_permission(self, request, view, obj):
        return request.user.pk == obj.user.pk
