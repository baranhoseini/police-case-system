from __future__ import annotations

from rest_framework.permissions import BasePermission

from rbac.models import UserRole

# Canonical role names as in the project document (section 2.2 "Flows")
CANONICAL_ROLE_ALIASES: dict[str, list[str]] = {
    # Admin / system owner
    "Administrator": ["Admin"],
    # Police org
    "Chief": [],
    "Captain": [],
    # Note: document uses "Sergent" (misspelling). Keep it canonical here.
    "Sergent": ["Sergeant"],
    "Detective": [],
    "Police Officer": ["Officer"],
    "Patrol Officer": ["Patrol"],
    "Cadet": [],
    # Public / case actors
    "Complainant": [],
    "Witness": [],
    "Suspect": [],
    "Criminal": [],
    # Judicial / medical
    "Judge": [],
    # Document uses "Corenary" (spelling). Keep it canonical here.
    "Corenary": ["Coroner"],
    # Base role
    "Base user": ["Citizen"],
    # Extra/legacy roles referenced in code
    "Supervisor": [],
}

# Build reverse alias lookup (alias -> canonical)
_ALIAS_TO_CANONICAL: dict[str, str] = {}
for canonical, aliases in CANONICAL_ROLE_ALIASES.items():
    _ALIAS_TO_CANONICAL[canonical] = canonical
    for a in aliases:
        _ALIAS_TO_CANONICAL[a] = canonical


def expand_role_names(*roles: str) -> list[str]:
    """Expand requested roles to include canonical + alias spellings.

    This keeps the project stable even if existing code checks legacy names like "Admin"/"Officer"
    while the DB stores canonical names like "Administrator"/"Police Officer".
    """
    expanded: list[str] = []
    for r in roles:
        if not r:
            continue
        canonical = _ALIAS_TO_CANONICAL.get(r, r)
        expanded.append(canonical)
        # add aliases for canonical
        for a in CANONICAL_ROLE_ALIASES.get(canonical, []):
            expanded.append(a)
    # de-duplicate preserving order
    seen=set()
    out=[]
    for r in expanded:
        if r not in seen:
            seen.add(r); out.append(r)
    return out


def canonicalize_role_name(name: str) -> str:
    """Map a role name (canonical or alias) to the document-canonical name if known."""
    return _ALIAS_TO_CANONICAL.get(name, name)


def user_has_role(user, *roles: str) -> bool:
    """RBAC helper.

    Superusers should always have access (useful for Django admin-created superusers).
    """
    if not user or not getattr(user, "is_authenticated", False):
        return False
    if getattr(user, "is_superuser", False):
        return True

    expanded = expand_role_names(*roles)
    return UserRole.objects.filter(user=user, role__name__in=expanded).exists()


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


# Common shortcut permissions used in some views
IsCadetRole = HasRole.with_roles("Cadet", "Admin", "Administrator")
IsOfficerRole = HasRole.with_roles("Officer", "Police Officer", "Admin", "Administrator")
