from rest_framework.permissions import SAFE_METHODS, BasePermission


class IsAdminOrReadOnly(BasePermission):
    def has_permission(self, request, view):
        user = request.user
        return (request.method in SAFE_METHODS
                or user.is_staff
                or user.is_superuser
                or user.is_admin
                )


class AuthorOrStaffOrReadOnly(BasePermission):
    def has_object_permission(self, request, view, obj):
        user = request.user
        return (request.method in SAFE_METHODS
                or user.is_staff
                or user.is_superuser
                or user.is_admin
                or obj.author == user)

    def has_permission(self, request, view):
        return request.method in SAFE_METHODS or request.user.is_authenticated


class OnlyAuthor(BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.author == request.user

    def has_permission(self, request, view):
        return request.user.is_authenticated
