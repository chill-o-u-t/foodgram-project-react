from rest_framework import permissions


class IsAdminOrAuthorOrReadOnly(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method not in permissions.SAFE_METHODS:
            return (
                request.user.is_authenticated
                and request.user == obj.author
                or request.user.is_admin
            )
        return True


class AdminOrReadOnly(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method not in permissions.SAFE_METHODS:
            return (
                request.user.is_authenticated
                and request.user.is_admin
            )
        return True
