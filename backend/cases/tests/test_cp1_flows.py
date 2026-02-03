from datetime import timedelta
from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework.test import APITestCase
from rest_framework import status

from rbac.models import Role, UserRole
from cases.models import Case
from suspects.models import Suspect
from rewards.models import RewardTip

User = get_user_model()

class CP1FlowTests(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.admin_role = Role.objects.create(name="Admin", description="Full access")
        cls.officer_role = Role.objects.create(name="Officer", description="Officer")
        cls.detective_role = Role.objects.create(name="Detective", description="Detective")
        cls.cadet_role = Role.objects.create(name="Cadet", description="Cadet")

        cls.citizen = User.objects.create_user(
            username="citizen",
            email="citizen@test.com",
            national_id="NID999",
            phone="0999",
            password="CitizenPassw0rd!!",
        )
        cls.officer = User.objects.create_user(
            username="officer",
            email="officer@test.com",
            password="OfficerPassw0rd!!",
        )
        cls.detective = User.objects.create_user(
            username="detective",
            email="detective@test.com",
            password="DetectivePassw0rd!!",
        )
        cls.cadet = User.objects.create_user(
            username="cadet",
            email="cadet@test.com",
            password="CadetPassw0rd!!",
        )
        cls.superuser = User.objects.create_superuser(
            username="super2",
            email="super2@test.com",
            password="SuperPassw0rd!!",
        )

        UserRole.objects.create(user=cls.officer, role=cls.officer_role)
        UserRole.objects.create(user=cls.detective, role=cls.detective_role)
        UserRole.objects.create(user=cls.cadet, role=cls.cadet_role)
        UserRole.objects.create(user=cls.superuser, role=cls.admin_role)

    def _create_case_as(self, user, title="Case 1"):
        self.client.force_authenticate(user=user)
        resp = self.client.post("/api/cases/", {"title": title, "description": "desc"}, format="json")
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        return resp.data["id"]

    def test_case_create_sets_created_by_and_open(self):
        case_id = self._create_case_as(self.citizen, "Case A")
        c = Case.objects.get(id=case_id)
        self.assertEqual(c.created_by_id, self.citizen.id)
        self.assertEqual(c.status, "OPEN")

    def test_complaint_create_and_three_strikes_invalidates_case(self):
        case_id = self._create_case_as(self.citizen, "Case Complaint")
        self.client.force_authenticate(user=self.citizen)
        resp = self.client.post(f"/api/cases/{case_id}/create_complaint/", {"details": "help"}, format="json")
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)

        self.client.force_authenticate(user=self.cadet)
        for _ in range(3):
            resp = self.client.post(f"/api/cases/{case_id}/complaint_strike/", {"reason": "bad"}, format="json")
            self.assertEqual(resp.status_code, status.HTTP_200_OK)

        c = Case.objects.get(id=case_id)
        self.assertEqual(c.status, "INVALIDATED")

    def test_crime_scene_requires_officer_role(self):
        case_id = self._create_case_as(self.citizen, "Case Scene")

        self.client.force_authenticate(user=self.citizen)
        resp = self.client.post(
            f"/api/cases/{case_id}/create_crime_scene/",
            {"report": "scene", "witnessed_phone": "1", "witnessed_national_id": "2"},
            format="json",
        )
        self.assertEqual(resp.status_code, status.HTTP_403_FORBIDDEN)

        self.client.force_authenticate(user=self.officer)
        resp = self.client.post(
            f"/api/cases/{case_id}/create_crime_scene/",
            {"report": "scene", "witnessed_phone": "1", "witnessed_national_id": "2"},
            format="json",
        )
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)

    def test_evidence_vehicle_constraint_rejects_plate_and_serial(self):
        case_id = self._create_case_as(self.officer, "Case Evidence")
        self.client.force_authenticate(user=self.officer)
        resp = self.client.post(
            "/api/evidence/",
            {
                "case": case_id,
                "evidence_type": "VEHICLE",
                "title": "car",
                "description": "desc",
                "vehicle_model": "BMW",
                "vehicle_color": "black",
                "plate_number": "ABC",
                "serial_number": "SER123",
                "id_fields": {},
                "image_url": "",
                "medical_result": "",
            },
            format="json",
        )
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    def test_evidence_vehicle_constraint_accepts_plate_only(self):
        case_id = self._create_case_as(self.officer, "Case Evidence OK")
        self.client.force_authenticate(user=self.officer)
        resp = self.client.post(
            "/api/evidence/",
            {
                "case": case_id,
                "evidence_type": "VEHICLE",
                "title": "car",
                "description": "desc",
                "vehicle_model": "BMW",
                "vehicle_color": "black",
                "plate_number": "ABC",
                "serial_number": "",
                "id_fields": {},
                "image_url": "",
                "medical_result": "",
            },
            format="json",
        )
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)

    def test_most_wanted_returns_only_over_30_days_sorted(self):
        case_id = self._create_case_as(self.officer, "Case Suspects")

        Suspect.objects.create(
            case_id=case_id,
            full_name="S1",
            chase_started_at=timezone.now() - timedelta(days=40),
            max_l=2,
            max_d=3,  # score=6
        )
        Suspect.objects.create(
            case_id=case_id,
            full_name="S2",
            chase_started_at=timezone.now() - timedelta(days=31),
            max_l=5,
            max_d=2,  # score=10
        )
        Suspect.objects.create(
            case_id=case_id,
            full_name="S3",
            chase_started_at=timezone.now() - timedelta(days=10),
            max_l=100,
            max_d=100,
        )

        self.client.force_authenticate(user=self.citizen)
        resp = self.client.get("/api/suspects/most-wanted/")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

        data = resp.json()
        self.assertEqual(len(data), 2)
        self.assertEqual(data[0]["full_name"], "S2")
        self.assertEqual(data[0]["rank_score"], 10)
        self.assertEqual(data[0]["reward_rials"], 10 * 20000000)

    def test_rewards_flow_submit_officer_review_detective_approve_and_lookup(self):
        self.client.force_authenticate(user=self.citizen)
        resp = self.client.post(
            "/api/rewards/tips/submit/",
            {"suspect_name": "X", "info": "I saw something"},
            format="json",
        )
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        tip_id = resp.data["id"]

        self.client.force_authenticate(user=self.officer)
        resp = self.client.post(
            f"/api/rewards/tips/{tip_id}/officer-review/",
            {"action": "approve"},
            format="json",
        )
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

        self.client.force_authenticate(user=self.detective)
        resp = self.client.post(
            f"/api/rewards/tips/{tip_id}/detective-approve/",
            {},
            format="json",
        )
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        code = resp.data["unique_code"]
        self.assertTrue(code)

        self.client.force_authenticate(user=self.officer)
        resp = self.client.get(f"/api/rewards/lookup/?national_id={self.citizen.national_id}&code={code}")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.data["tip_id"], tip_id)

    def test_stats_endpoint_returns_expected_keys(self):
        self._create_case_as(self.officer, "Case Stats")
        RewardTip.objects.create(citizen=self.citizen, suspect_name="Z", info="tip")

        self.client.force_authenticate(user=self.officer)
        resp = self.client.get("/api/stats/")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

        self.assertIn("cases_open", resp.data)
        self.assertIn("cases_closed", resp.data)
        self.assertIn("most_wanted", resp.data)
        self.assertIn("tips_pending", resp.data)
