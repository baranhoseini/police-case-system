from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import RefreshToken

from rbac.models import Role, UserRole
from payments.models import PaymentRequest

User = get_user_model()


class PaymentE2EFlowTests(APITestCase):
    def setUp(self):
        # Create sergeant role (spelling can vary; we create both for safety)
        self.role_sergent, _ = Role.objects.get_or_create(name="Sergent")
        self.role_sergeant, _ = Role.objects.get_or_create(name="Sergeant")

        # Create users
        self.sergent = User.objects.create_user(
            username="sergent_user",
            password="StrongPass123!",
            email="sergent_user@example.com",
            phone="SERGENT_PHONE",
            first_name="Ser",
            last_name="Gent",
            national_id="SERGENT_NID",
        )
        self.payer = User.objects.create_user(
            username="payer_user",
            password="StrongPass123!",
            email="payer_user@example.com",
            phone="PAYER_PHONE",
            first_name="Pay",
            last_name="Er",
            national_id="PAYER_NID",
        )

        # Assign sergeant role (either spelling acceptable)
        UserRole.objects.get_or_create(user=self.sergent, role=self.role_sergent)

        # Tokens
        self.sergent_access = str(RefreshToken.for_user(self.sergent).access_token)
        self.payer_access = str(RefreshToken.for_user(self.payer).access_token)

    def auth(self, token: str):
        return {"HTTP_AUTHORIZATION": f"Bearer {token}"}

    def test_bail_level2_full_flow_paid(self):
        """
        Full flow:
          sergent creates BAIL request (level 2 allowed)
          payer initiates -> redirect_url returned
          simulate callback -> status becomes PAID
          payer fetches status -> PAID
        """
        # 1) Create request (sergent)
        res = self.client.post(
            "/payments/api/requests/",
            {
                "payer_user_id": self.payer.id,
                "purpose": "BAIL",
                "amount_rials": 5_000_000,
                "crime_level": 2,
            },
            format="json",
            **self.auth(self.sergent_access),
        )
        self.assertEqual(res.status_code, 201, res.data)
        pr_id = res.data["id"]

        # 2) Initiate (payer)
        res = self.client.post(
            f"/payments/api/requests/{pr_id}/initiate/",
            {},
            format="json",
            **self.auth(self.payer_access),
        )
        self.assertEqual(res.status_code, 200, res.data)
        self.assertIn("redirect_url", res.data)

        pr = PaymentRequest.objects.get(id=pr_id)
        self.assertEqual(pr.status, PaymentRequest.STATUS_INITIATED)

        # 3) Simulate gateway callback success
        cb = self.client.get(f"/payments/callback/?payment_id={pr.public_id}&status=ok&ref_id=MOCK_REF")
        self.assertEqual(cb.status_code, 200)

        pr.refresh_from_db()
        self.assertEqual(pr.status, PaymentRequest.STATUS_PAID)
        self.assertEqual(pr.ref_id, "MOCK_REF")

        # 4) Get status (payer)
        res = self.client.get(
            f"/payments/api/requests/{pr_id}/",
            format="json",
            **self.auth(self.payer_access),
        )
        self.assertEqual(res.status_code, 200, res.data)
        self.assertEqual(res.data["status"], PaymentRequest.STATUS_PAID)

    def test_bail_disallowed_level1(self):
        """
        Bail allowed only for level 2 or 3.
        """
        res = self.client.post(
            "/payments/api/requests/",
            {
                "payer_user_id": self.payer.id,
                "purpose": "BAIL",
                "amount_rials": 1_000_000,
                "crime_level": 1,
            },
            format="json",
            **self.auth(self.sergent_access),
        )
        self.assertEqual(res.status_code, 400, res.data)

    def test_fine_requires_level3_and_approval(self):
        """
        Fine allowed only for level 3 and must be approved before initiate.
        """
        # 1) Create fine request (level 3 ok)
        res = self.client.post(
            "/payments/api/requests/",
            {
                "payer_user_id": self.payer.id,
                "purpose": "FINE",
                "amount_rials": 7_000_000,
                "crime_level": 3,
            },
            format="json",
            **self.auth(self.sergent_access),
        )
        self.assertEqual(res.status_code, 201, res.data)
        pr_id = res.data["id"]

        # 2) Initiate before approval -> 409
        res = self.client.post(
            f"/payments/api/requests/{pr_id}/initiate/",
            {},
            format="json",
            **self.auth(self.payer_access),
        )
        self.assertEqual(res.status_code, 409, res.data)

        # 3) Approve (sergent)
        res = self.client.post(
            f"/payments/api/requests/{pr_id}/approve/",
            {},
            format="json",
            **self.auth(self.sergent_access),
        )
        self.assertEqual(res.status_code, 200, res.data)

        # 4) Initiate after approval -> 200
        res = self.client.post(
            f"/payments/api/requests/{pr_id}/initiate/",
            {},
            format="json",
            **self.auth(self.payer_access),
        )
        self.assertEqual(res.status_code, 200, res.data)
        self.assertIn("redirect_url", res.data)

    def test_fine_disallowed_level2(self):
        """
        Fine allowed only for level 3.
        """
        res = self.client.post(
            "/payments/api/requests/",
            {
                "payer_user_id": self.payer.id,
                "purpose": "FINE",
                "amount_rials": 2_000_000,
                "crime_level": 2,
            },
            format="json",
            **self.auth(self.sergent_access),
        )
        self.assertEqual(res.status_code, 400, res.data)