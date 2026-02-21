from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import RefreshToken

from rbac.models import Role, UserRole

User = get_user_model()


def make_user(
    *,
    username: str,
    password: str = "StrongPass123!",
    email: str,
    phone: str,
    national_id: str,
    first_name: str = "T",
    last_name: str = "U",
    is_superuser: bool = False,
    is_staff: bool = False,
):
    u = User.objects.create_user(
        username=username,
        password=password,
        email=email,
        phone=phone,
        national_id=national_id,
        first_name=first_name,
        last_name=last_name,
    )
    if is_superuser:
        u.is_superuser = True
        u.is_staff = True
        u.save(update_fields=["is_superuser", "is_staff"])
    elif is_staff:
        u.is_staff = True
        u.save(update_fields=["is_staff"])
    return u


def token_for(user) -> str:
    return str(RefreshToken.for_user(user).access_token)


def auth_header(token: str) -> dict:
    return {"HTTP_AUTHORIZATION": f"Bearer {token}"}


def grant_role(user, role_name: str):
    role, _ = Role.objects.get_or_create(name=role_name)
    UserRole.objects.get_or_create(user=user, role=role)
    return role