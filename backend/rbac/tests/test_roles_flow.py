# backend/rbac/tests/test_roles_flow.py
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.core.management import call_command

from rbac.models import Role, UserRole


class RolesFlowTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        # Make sure roles exist
        call_command("seed_roles")

    def create_user(self, username, email, phone, national_id, password="Passw0rd!!"):
        User = get_user_model()
        u = User.objects.create(
            username=username,
            email=email,
            first_name="Test",
            last_name="User",
            phone=phone,
            national_id=national_id,
        )
        u.set_password(password)
        u.is_active = True
        u.save()
        return u, password

    def login(self, identifier, password):
        return self.client.post(
            "/api/auth/login/",
            data={"identifier": identifier, "password": password},
            content_type="application/json",
        )

    def me(self, token):
        return self.client.get("/api/auth/me/", HTTP_AUTHORIZATION=f"Bearer {token}")

    def assign_role(self, token, user_id, role_name):
        return self.client.post(
            "/api/rbac/assign-role/",
            data={"user_id": user_id, "role_name": role_name},
            content_type="application/json",
            HTTP_AUTHORIZATION=f"Bearer {token}",
        )

    def test_seed_roles_created_expected(self):
        self.assertGreater(Role.objects.count(), 0)
        for r in ["Admin", "Citizen", "Detective", "Officer", "Judge"]:
            self.assertTrue(Role.objects.filter(name=r).exists(), f"Missing role: {r}")

    def test_login_returns_roles_and_primary_role(self):
        u, pw = self.create_user(
            username="u1",
            email="u1@test.com",
            phone="09120000001",
            national_id="1234567890",
        )
        # Give base role
        citizen = Role.objects.get(name="Citizen")
        UserRole.objects.get_or_create(user=u, role=citizen)

        res = self.login("u1@test.com", pw)
        self.assertEqual(res.status_code, 200, res.content)

        data = res.json()
        self.assertIn("access", data)
        self.assertIn("user", data)

        user_json = data["user"]
        self.assertIn("roles", user_json)
        self.assertIn("primary_role", user_json)
        self.assertIn("Base user", user_json["roles"])

    def test_assign_role_forbidden_for_non_admin(self):
        u, pw = self.create_user(
            username="normal",
            email="normal@test.com",
            phone="09120000002",
            national_id="2234567890",
        )
        citizen = Role.objects.get(name="Citizen")
        UserRole.objects.get_or_create(user=u, role=citizen)

        login = self.login("normal@test.com", pw)
        self.assertEqual(login.status_code, 200, login.content)
        token = login.json()["access"]

        res = self.assign_role(token, u.id, "Judge")
        self.assertIn(res.status_code, (401, 403), res.content)

    def test_admin_can_assign_role_and_me_updates(self):
        admin, admin_pw = self.create_user(
            username="admin_test",
            email="admin_test@test.com",
            phone="09120000003",
            national_id="3234567890",
        )
        admin_role = Role.objects.get(name="Admin")
        UserRole.objects.get_or_create(user=admin, role=admin_role)

        target, target_pw = self.create_user(
            username="target",
            email="target@test.com",
            phone="09120000004",
            national_id="4234567890",
        )
        citizen = Role.objects.get(name="Citizen")
        UserRole.objects.get_or_create(user=target, role=citizen)

        admin_login = self.login("admin_test@test.com", admin_pw)
        self.assertEqual(admin_login.status_code, 200, admin_login.content)
        admin_token = admin_login.json()["access"]

        assign = self.assign_role(admin_token, target.id, "Judge")
        self.assertIn(assign.status_code, (200, 201), assign.content)

        target_login = self.login("target@test.com", target_pw)
        self.assertEqual(target_login.status_code, 200, target_login.content)
        target_token = target_login.json()["access"]

        me = self.me(target_token)
        self.assertEqual(me.status_code, 200, me.content)
        me_json = me.json()
        self.assertIn("Judge", me_json.get("roles", []))
        self.assertIn(me_json.get("primary_role"), me_json.get("roles", []))


    def test_document_role_name_mapping(self):
      # Create a user with internal role names in DB
      u, pw = self.create_user(
        username="map1",
        email="map1@test.com",
        phone="09120009990",
        national_id="9999999990",
      )
      # assign internal role
      UserRole.objects.get_or_create(user=u, role=Role.objects.get(name="Citizen"))

      res = self.login("map1@test.com", pw)
      self.assertEqual(res.status_code, 200, res.content)
      roles = res.json()["user"]["roles"]

      # Expect document label
      self.assertIn("Base user", roles)

    def test_me_returns_roles_and_primary_role(self):
      u, pw = self.create_user(
        username="me1",
        email="me1@test.com",
        phone="09120009991",
        national_id="9999999991",
      )
      UserRole.objects.get_or_create(user=u, role=Role.objects.get(name="Citizen"))

      login = self.login("me1@test.com", pw)
      token = login.json()["access"]

      me = self.me(token)
      self.assertEqual(me.status_code, 200, me.content)
      me_json = me.json()
      self.assertIn("roles", me_json)
      self.assertIn("primary_role", me_json)