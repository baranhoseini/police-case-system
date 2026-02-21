from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import RefreshToken

from rbac.models import Role

User = get_user_model()


class RBACChangeabilityTests(APITestCase):
    def setUp(self):
        # Use a superuser so role CRUD isn't blocked by permission rules.
        self.admin = User.objects.create_user(
            username="admin",
            password="StrongPass123!",
            email="admin@example.com",
            phone="ADMIN_PHONE",
            national_id="ADMIN_NID",
            first_name="A",
            last_name="D",
        )
        self.admin.is_superuser = True
        self.admin.is_staff = True
        self.admin.save(update_fields=["is_superuser", "is_staff"])

        self.admin_token = str(RefreshToken.for_user(self.admin).access_token)

        self.user = User.objects.create_user(
            username="userx",
            password="StrongPass123!",
            email="userx@example.com",
            phone="USERX_PHONE",
            national_id="USERX_NID",
            first_name="U",
            last_name="X",
        )

    def auth(self):
        return {"HTTP_AUTHORIZATION": f"Bearer {self.admin_token}"}

    def test_create_assign_revoke_role_without_code_change(self):
        # Create new role (changeability) :contentReference[oaicite:10]{index=10}
        res = self.client.post("/api/rbac/roles/", {"name": "NewRole", "description": "tmp"}, format="json", **self.auth())
        self.assertIn(res.status_code, (200, 201), res.data)
        self.assertTrue(Role.objects.filter(name="NewRole").exists())

        # Assign
        res = self.client.post(
            "/api/rbac/assign-role/",
            {"user_id": self.user.id, "role_name": "NewRole"},
            format="json",
            **self.auth(),
        )
        self.assertIn(res.status_code, (200, 201), res.data)

        # Verify roles endpoint
        res = self.client.get("/api/rbac/me/roles/", **self.auth())
        self.assertEqual(res.status_code, 200)

        # Revoke
        res = self.client.post(
            "/api/rbac/revoke-role/",
            {"user_id": self.user.id, "role_name": "NewRole"},
            format="json",
            **self.auth(),
        )
        self.assertIn(res.status_code, (200, 204), res.data)