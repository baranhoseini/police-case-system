from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase
from rest_framework import status

from rbac.models import Role, UserRole

User = get_user_model()

class AuthRBACTests(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.admin_role = Role.objects.create(name="Admin", description="Full access")
        cls.superuser = User.objects.create_superuser(
            username="super1", email="super1@test.com", password="SuperPassw0rd!!"
        )
        cls.user = User.objects.create_user(
            username="user1",
            email="user1@test.com",
            national_id="NID1",
            phone="P1",
            password="UserPassw0rd!!",
        )

    def test_register_creates_user(self):
        resp = self.client.post(
            "/api/auth/register/",
            {
                "username": "baran2",
                "email": "baran2@test.com",
                "phone": "222",
                "national_id": "222",
                "password": "Passw0rd!!",
            },
            format="json",
        )
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        self.assertEqual(resp.data["username"], "baran2")

    def test_login_by_email_returns_tokens(self):
        resp = self.client.post(
            "/api/auth/login/",
            {"identifier": "user1@test.com", "password": "UserPassw0rd!!"},
            format="json",
        )
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertIn("access", resp.data)
        self.assertIn("refresh", resp.data)

    def test_login_by_username_returns_tokens(self):
        resp = self.client.post(
            "/api/auth/login/",
            {"identifier": "user1", "password": "UserPassw0rd!!"},
            format="json",
        )
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertIn("access", resp.data)

    def test_me_requires_auth(self):
        resp = self.client.get("/api/auth/me/")
        self.assertEqual(resp.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_rbac_roles_requires_admin_or_superuser(self):
        self.client.force_authenticate(user=self.user)
        resp = self.client.get("/api/rbac/roles/")
        self.assertEqual(resp.status_code, status.HTTP_403_FORBIDDEN)

        self.client.force_authenticate(user=self.superuser)
        resp = self.client.get("/api/rbac/roles/")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

        UserRole.objects.create(user=self.user, role=self.admin_role)
        self.client.force_authenticate(user=self.user)
        resp = self.client.get("/api/rbac/roles/")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
