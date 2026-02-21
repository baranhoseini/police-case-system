from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model

User = get_user_model()


class AuthContractTests(APITestCase):
    def test_register_requires_all_doc_fields_and_creates_user(self):
        # Spec: username, password, email, phone, first/last, national_id :contentReference[oaicite:8]{index=8}
        res = self.client.post(
            "/api/auth/register/",
            {
                "username": "u1",
                "password": "StrongPass123!",
                "email": "u1@example.com",
                "phone": "+49000000001",
                "first_name": "A",
                "last_name": "B",
                "national_id": "NID001",
            },
            format="json",
        )
        self.assertIn(res.status_code, (200, 201), res.data)
        self.assertTrue(User.objects.filter(username="u1").exists())

    def test_register_unique_identifiers_enforced(self):
        self.client.post(
            "/api/auth/register/",
            {
                "username": "u2",
                "password": "StrongPass123!",
                "email": "dup@example.com",
                "phone": "+49000000002",
                "first_name": "A",
                "last_name": "B",
                "national_id": "NID002",
            },
            format="json",
        )
        # Duplicate email/phone/national_id should fail :contentReference[oaicite:9]{index=9}
        res = self.client.post(
            "/api/auth/register/",
            {
                "username": "u3",
                "password": "StrongPass123!",
                "email": "dup@example.com",
                "phone": "+49000000002",
                "first_name": "A",
                "last_name": "B",
                "national_id": "NID002",
            },
            format="json",
        )
        self.assertEqual(res.status_code, 400, res.data)

    def _login(self, identifier: str, password: str):
        return self.client.post(
            "/api/auth/login/",
            {"identifier": identifier, "password": password},
            format="json",
        )

    def test_login_by_all_identifiers(self):
        self.client.post(
            "/api/auth/register/",
            {
                "username": "u4",
                "password": "StrongPass123!",
                "email": "u4@example.com",
                "phone": "+49000000004",
                "first_name": "A",
                "last_name": "B",
                "national_id": "NID004",
            },
            format="json",
        )

        for identifier in ["u4", "u4@example.com", "+49000000004", "NID004"]:
            res = self._login(identifier, "StrongPass123!")
            self.assertEqual(res.status_code, 200, res.data)
            self.assertIn("access", res.data)
            self.assertIn("refresh", res.data)