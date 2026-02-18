# rewards/views.py
import uuid

from django.shortcuts import get_object_or_404
from django.utils import timezone


from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from config.permissions import HasRole
from suspects.models import Suspect
from .models import RewardTip

# All police roles available in your system:
POLICE_ROLES = ("Admin", "Cadet", "Chief", "Detective", "Officer", "Supervisor")

IsPoliceRole = HasRole.with_roles(*POLICE_ROLES)
IsOfficerLevel = HasRole.with_roles("Officer", "Admin", "Chief", "Supervisor")
IsDetectiveLevel = HasRole.with_roles("Detective", "Admin", "Chief", "Supervisor")


def _generate_unique_code() -> str:
    """
    Generate a short code that is easy to type/share.
    """
    return uuid.uuid4().hex[:12]


class SubmitTip(APIView):
    """
    POST /api/rewards/tips/submit/
    Authenticated users submit a tip.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        citizen_name = request.data.get("citizen_name")
        citizen_national_id = request.data.get("citizen_national_id")
        citizen_phone = request.data.get("citizen_phone")

        suspect_name = request.data.get("suspect_name")
        suspect_last_seen = request.data.get("suspect_last_seen")
        message = request.data.get("message")

        required_fields = ["citizen_name", "citizen_national_id", "citizen_phone", "suspect_name", "message"]
        missing = [f for f in required_fields if not request.data.get(f)]
        if missing:
            return Response(
                {"detail": f"Missing fields: {', '.join(missing)}"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        tip = RewardTip.objects.create(
            citizen=request.user,
            citizen_name=citizen_name,
            citizen_national_id=citizen_national_id,
            citizen_phone=citizen_phone,
            suspect_name=suspect_name,
            suspect_last_seen=suspect_last_seen or "",
            message=message,
            status=RewardTip.STATUS_SUBMITTED,
        )

        return Response(
            {"tip_id": tip.id, "status": tip.status},
            status=status.HTTP_201_CREATED,
        )


class OfficerReviewTip(APIView):
    """
    POST /api/rewards/tips/<tip_id>/officer-review/
    body: { "decision": "approve" | "reject", "note": "..." }
    Restricted to Officer/Admin/Chief/Supervisor.
    """
    permission_classes = [IsOfficerLevel]

    def post(self, request, tip_id: int):
        tip = get_object_or_404(RewardTip, id=tip_id)

        if tip.status != RewardTip.STATUS_SUBMITTED:
            return Response(
                {"detail": f"Tip is not in SUBMITTED state (current={tip.status})."},
                status=status.HTTP_409_CONFLICT,
            )

        decision = (request.data.get("decision") or "").lower().strip()
        note = request.data.get("note") or ""

        if decision not in ("approve", "reject"):
            return Response(
                {"detail": "decision must be 'approve' or 'reject'."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        tip.reviewed_by_officer = request.user
        tip.officer_reviewed_at = timezone.now()
        tip.officer_note = note

        if decision == "approve":
            tip.status = RewardTip.STATUS_OFFICER_APPROVED
        else:
            tip.status = RewardTip.STATUS_OFFICER_REJECTED

        tip.save(update_fields=["reviewed_by_officer", "officer_reviewed_at", "officer_note", "status"])

        return Response({"tip_id": tip.id, "status": tip.status}, status=status.HTTP_200_OK)


class DetectiveApproveTip(APIView):
    """
    POST /api/rewards/tips/<tip_id>/detective-approve/
    body: { "note": "..." }
    Restricted to Detective/Admin/Chief/Supervisor.
    Generates and returns a unique_code when approved.
    """
    permission_classes = [IsDetectiveLevel]

    def post(self, request, tip_id: int):
        tip = get_object_or_404(RewardTip, id=tip_id)

        if tip.status != RewardTip.STATUS_OFFICER_APPROVED:
            return Response(
                {"detail": f"Tip is not in OFFICER_APPROVED state (current={tip.status})."},
                status=status.HTTP_409_CONFLICT,
            )

        note = request.data.get("note") or ""

        # Generate a unique code (retry a few times in case of collision)
        code = _generate_unique_code()
        for _ in range(5):
            if not RewardTip.objects.filter(unique_code=code).exists():
                break
            code = _generate_unique_code()

        tip.unique_code = code
        tip.approved_by_detective = request.user
        tip.detective_approved_at = timezone.now()
        tip.detective_note = note
        tip.status = RewardTip.STATUS_DETECTIVE_APPROVED

        tip.save(update_fields=["unique_code", "approved_by_detective", "detective_approved_at", "detective_note", "status"])

        return Response(
            {"tip_id": tip.id, "status": tip.status, "unique_code": tip.unique_code},
            status=status.HTTP_200_OK,
        )


class RewardLookup(APIView):
    """
    GET /api/rewards/lookup/?citizen_national_id=...&unique_code=...

    Must be accessible by ALL police ranks.
    Must return reward_amount and citizen details.
    """
    permission_classes = [IsPoliceRole]

    def get(self, request):
        citizen_national_id = request.query_params.get("citizen_national_id") or request.data.get("citizen_national_id")
        unique_code = request.query_params.get("unique_code") or request.data.get("unique_code")

        if not citizen_national_id or not unique_code:
            return Response(
                {"detail": "citizen_national_id and unique_code are required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        tip = (
            RewardTip.objects.filter(
                citizen_national_id=citizen_national_id,
                unique_code=unique_code,
                status=RewardTip.STATUS_DETECTIVE_APPROVED,
            )
            .order_by("-detective_approved_at", "-id")
            .first()
        )

        if not tip:
            return Response(
                {"detail": "No detective-approved tip found for the given citizen_national_id and unique_code."},
                status=status.HTTP_404_NOT_FOUND,
            )

        # Match suspect by name (best-effort).
        suspect = Suspect.objects.filter(full_name__iexact=tip.suspect_name).order_by("-chase_started_at", "-id").first()

        # Your Suspect model computes reward in rials: reward_amount_rials
        # Keep API key as "reward_amount" (as tests usually expect).
        reward_amount = int(getattr(suspect, "reward_amount_rials", 0)) if suspect else 0

        return Response(
            {
                "reward_amount": reward_amount,
                "citizen": {
                    "name": tip.citizen_name,
                    "national_id": tip.citizen_national_id,
                    "phone": tip.citizen_phone,
                },
                "tip": {
                    "id": tip.id,
                    "suspect_name": tip.suspect_name,
                    "suspect_last_seen": tip.suspect_last_seen,
                    "message": tip.message,
                    "status": tip.status,
                    "created_at": tip.created_at,
                },
                "unique_code": tip.unique_code,
            },
            status=status.HTTP_200_OK,
        )
