from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import RefreshToken

User = get_user_model()


class EvidenceSpecTests(APITestCase):
    def setUp(self):
        self.u = User.objects.create_user(
            username="ev_user",
            password="StrongPass123!",
            email="ev@example.com",
            phone="EV_PHONE",
            national_id="EV_NID",
            first_name="E",
            last_name="V",
        )
        self.token = str(RefreshToken.for_user(self.u).access_token)

        # Evidence requires a case
        case_resp = self.client.post(
            "/api/cases/",
            {"title": "Case for evidence", "description": "desc"},
            format="json",
            HTTP_AUTHORIZATION=f"Bearer {self.token}",
        )
        assert case_resp.status_code in (200, 201), case_resp.data
        self.case_id = case_resp.data["id"]

    def auth(self):
        return {"HTTP_AUTHORIZATION": f"Bearer {self.token}"}

    def test_vehicle_plate_xor_serial(self):
        # Your API uses plate_number / serial_number and requires case
        ok = self.client.post(
            "/api/evidence/",
            {
                "case": self.case_id,
                "title": "Car",
                "description": "plate only",
                "evidence_type": "VEHICLE",
                "plate_number": "ABC123",
                "serial_number": "",
            },
            format="json",
            **self.auth(),
        )
        self.assertIn(ok.status_code, (200, 201), ok.data)

        bad = self.client.post(
            "/api/evidence/",
            {
                "case": self.case_id,
                "title": "Car2",
                "description": "both set",
                "evidence_type": "VEHICLE",
                "plate_number": "ABC123",
                "serial_number": "SER123",
            },
            format="json",
            **self.auth(),
        )
        self.assertEqual(bad.status_code, 400, bad.data)

    def test_id_evidence_key_value_optional(self):
        # Your API uses evidence_type=ID_DOC and id_fields is key-value (can be empty)
        res = self.client.post(
            "/api/evidence/",
            {
                "case": self.case_id,
                "title": "ID Card",
                "description": "no extra fields",
                "evidence_type": "ID_DOC",
                "id_fields": {},  # optional / can be empty
            },
            format="json",
            **self.auth(),
        )
        self.assertIn(res.status_code, (200, 201), res.data)