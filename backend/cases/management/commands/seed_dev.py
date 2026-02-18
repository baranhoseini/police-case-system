from __future__ import annotations

from django.apps import apps
from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.utils import timezone


def M(app_label: str, model_name: str):
    try:
        return apps.get_model(app_label, model_name)
    except Exception:
        return None


class Command(BaseCommand):
    help = "Seed development data (cases/evidence/rewards) based on current project models."

    def add_arguments(self, parser):
        parser.add_argument("--reset", action="store_true", help="Delete existing seeded data before creating new.")

    def handle(self, *args, **opts):
        reset = opts["reset"]
        User = get_user_model()

        Case = M("cases", "Case")
        Complaint = M("cases", "Complaint")
        CrimeSceneReport = M("cases", "CrimeSceneReport")
        DetectiveBoard = M("cases", "DetectiveBoard")
        DetectiveBoardItem = M("cases", "DetectiveBoardItem")
        SolveRequest = M("cases", "SolveRequest")
        Interrogation = M("cases", "Interrogation")
        CaptainDecision = M("cases", "CaptainDecision")
        Trial = M("cases", "Trial")

        Evidence = M("evidence", "Evidence")
        RewardTip = M("rewards", "RewardTip")

        if reset:
            self.stdout.write(self.style.WARNING("Resetting (best effort)..."))
            for mdl in [
                DetectiveBoardItem,
                DetectiveBoard,
                Evidence,
                RewardTip,
                Trial,
                CaptainDecision,
                Interrogation,
                SolveRequest,
                CrimeSceneReport,
                Complaint,
                Case,
            ]:
                if mdl:
                    try:
                        mdl.objects.all().delete()
                    except Exception:
                        pass

        def upsert_user(username, password, **extra):
            defaults = dict(extra)

            phone = defaults.get("phone")
            national_id = defaults.get("national_id")
            email = defaults.get("email")

            user = None

            try:
                user = User.objects.get(username=username)
            except Exception:
                user = None

            if user is None and phone:
                try:
                    user = User.objects.get(phone=phone)
                except Exception:
                    user = None

            if user is None and national_id:
                try:
                    user = User.objects.get(national_id=national_id)
                except Exception:
                    user = None

            if user is None and email:
                try:
                    user = User.objects.get(email=email)
                except Exception:
                    user = None

            if user is None:
                user = User(username=username, **defaults)
            else:
                for k, v in defaults.items():
                    if hasattr(user, k) and v is not None and getattr(user, k) != v:
                        setattr(user, k, v)

                if getattr(user, "username", None) != username:
                    try:
                        if not User.objects.filter(username=username).exclude(pk=user.pk).exists():
                            user.username = username
                    except Exception:
                        pass

            user.set_password(password)
            user.save()
            return user

        admin = upsert_user(
            "admin",
            "admin1234",
            email="admin@example.com",
            phone="09120000000",
            national_id="0011111111",
            is_staff=True,
            is_superuser=True,
        )
        officer = upsert_user(
            "officer1",
            "Pass1234!",
            email="officer1@example.com",
            phone="09120000002",
            national_id="0011111113",
        )
        detective = upsert_user(
            "detective1",
            "Pass1234!",
            email="detective1@example.com",
            phone="09120000003",
            national_id="0011111114",
        )
        citizen = upsert_user(
            "citizen1",
            "Pass1234!",
            email="citizen1@example.com",
            phone="09120000006",
            national_id="0011111117",
        )

        if not Case:
            self.stdout.write(self.style.ERROR("cases.Case not found -> cannot seed."))
            return

        c1, _ = Case.objects.get_or_create(
            title="[DEV] Bank Robbery",
            defaults={
                "description": "Seed case for frontend.",
                "status": "OPEN",
                "crime_level": 2,
                "created_by": officer,
                "created_at": timezone.now(),
            },
        )
        c2, _ = Case.objects.get_or_create(
            title="[DEV] Missing Person",
            defaults={
                "description": "Seed case for frontend.",
                "status": "UNDER_REVIEW",
                "crime_level": 1,
                "created_by": detective,
                "created_at": timezone.now(),
            },
        )

        if Complaint:
            Complaint.objects.get_or_create(
                case=c1,
                defaults={"complainant": citizen, "details": "Citizen reported a robbery with masked suspects."},
            )

        if CrimeSceneReport:
            CrimeSceneReport.objects.get_or_create(
                case=c1,
                defaults={
                    "reporter": officer,
                    "report": "Arrived at the scene. CCTV requested. Witness saw black sedan.",
                    "witnessed_phone": "09123334444",
                    "witnessed_national_id": "0022222222",
                    "is_approved": True,
                    "approved_by": detective,
                    "approved_at": timezone.now(),
                },
            )

        if DetectiveBoard:
            b1, _ = DetectiveBoard.objects.get_or_create(case=c1, defaults={"created_by": detective})
            if DetectiveBoardItem:
                DetectiveBoardItem.objects.get_or_create(
                    board=b1,
                    item_type="NOTE",
                    title="Start Here",
                    defaults={
                        "content": "Seed board note for UI.",
                        "x": 120,
                        "y": 80,
                        "meta": {},
                        "created_by": detective,
                    },
                )

        if Evidence:
            Evidence.objects.get_or_create(
                case=c1,
                evidence_type="MEDICAL",
                title="Blood sample photo",
                defaults={
                    "description": "Medical evidence with at least one image.",
                    "created_by": detective,
                    "image_urls": ["https://example.com/blood1.jpg"],
                    "image_url": "https://example.com/blood1.jpg",
                },
            )
            Evidence.objects.get_or_create(
                case=c1,
                evidence_type="VEHICLE",
                title="Getaway car info",
                defaults={
                    "description": "Vehicle evidence with plate XOR serial.",
                    "created_by": officer,
                    "vehicle_model": "Sedan",
                    "vehicle_color": "Black",
                    "plate_number": "12A345-67",
                },
            )

        if SolveRequest:
            SolveRequest.objects.get_or_create(
                case=c1,
                status="SUBMITTED",
                defaults={
                    "suspect_ids": [],
                    "note": "Request to close case (seed).",
                    "submitted_by": detective,
                    "submitted_at": timezone.now(),
                },
            )

        if Interrogation:
            try:
                Interrogation.objects.get_or_create(
                    case=c1,
                    suspect_id=1,
                    defaults={"detective_score": 7, "sergent_score": 6},
                )
            except Exception:
                pass

        if CaptainDecision:
            CaptainDecision.objects.get_or_create(
                case=c2,
                defaults={
                    "decision": "SEND_TO_TRIAL",
                    "comment": "Seed decision.",
                    "decided_by": detective,
                    "decided_at": timezone.now(),
                    "chief_approved": True,
                    "chief_by": admin,
                    "chief_at": timezone.now(),
                    "chief_comment": "Approved (seed).",
                },
            )

        if Trial:
            Trial.objects.get_or_create(
                case=c2,
                defaults={
                    "verdict": "GUILTY",
                    "punishment_title": "Prison",
                    "punishment_description": "10 years imprisonment (seed).",
                    "judged_by": admin,
                    "judged_at": timezone.now(),
                },
            )

        if RewardTip:
            status_value = getattr(RewardTip, "STATUS_SUBMITTED", "SUBMITTED")
            RewardTip.objects.get_or_create(
                citizen=citizen,
                citizen_name="Citizen One",
                citizen_national_id="0011111117",
                citizen_phone="09120000006",
                suspect_name="Unknown Suspect",
                defaults={
                    "suspect_last_seen": "Near old warehouse",
                    "message": "I saw the suspect around 10pm.",
                    "status": status_value,
                },
            )

        self.stdout.write(self.style.SUCCESS("Seed done. admin/admin1234 , others: Pass1234!"))
