from __future__ import annotations

from rest_framework.permissions import BasePermission

from rbac.models import UserRole


def user_has_role(user, *roles: str) -> bool:
    """RBAC helper.

    Superusers should always have access (useful for Django admin-created superusers).
    """
    if not user or not getattr(user, "is_authenticated", False):
        return False
    if getattr(user, "is_superuser", False):
        return True
    return UserRole.objects.filter(user=user, role__name__in=roles).exists()


class HasRole(BasePermission):
    allowed_roles: list[str] = []

    def has_permission(self, request, view) -> bool:
        return user_has_role(request.user, *self.allowed_roles)

    @classmethod
    def with_roles(cls, *roles: str):
        class RolePermission(cls):
            allowed_roles = list(roles)

        RolePermission.__name__ = f"{cls.__name__}_{'_'.join(roles)}"
        RolePermission.__qualname__ = RolePermission.__name__
        return RolePermission


IsCadetRole = HasRole.with_roles("Cadet", "Admin")
IsOfficerRole = HasRole.with_roles("Officer", "Admin")