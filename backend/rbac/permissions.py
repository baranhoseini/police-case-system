from rest_framework.permissions import BasePermission
from rbac.models import UserRole

class HasRole(BasePermission):
    required_roles = []

    @classmethod
    def with_roles(cls, *roles):
        class _HasRole(cls):
            required_roles = list(roles)
        return _HasRole

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False

        # Bootstrap: superuser can access admin-only endpoints

        if getattr(request.user, "is_superuser", False):
            return True

        return UserRole.objects.filter(
            user=request.user,
            role__name__in=self.required_roles
        ).exists()
