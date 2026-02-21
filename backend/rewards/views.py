from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from config.permissions import HasRole
from suspects.models import Suspect
from .models import RewardTip

POLICE_ROLES = ("Admin", "Cadet", "Officer", "Detective", "Chief", "Captain", "Supervisor")
IsPoliceRole = HasRole.with_roles(*POLICE_ROLES)
IsOfficerLevel = HasRole.with_roles("Officer", "Admin", "Chief", "Captain", "Supervisor")
IsDetectiveLevel = HasRole.with_roles("Detective", "Admin", "Chief", "Captain", "Supervisor")


class SubmitTip(APIView):
    """Citizen submits a reward tip.

    Accepts:
      - suspect_name
      - info  (compatible with tests)
    Also supports:
      - message
      - suspect_last_seen
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        suspect_name = (request.data.get("suspect_name") or "").strip()
        info = (request.data.get("info") or request.data.get("message") or "").strip()
        suspect_last_seen = (request.data.get("suspect_last_seen") or "").strip()

        if not suspect_name or not info:
            return Response(
                {"detail": "suspect_name and info are required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        u = request.user
        citizen_name = (f"{getattr(u, 'first_name', '')} {getattr(u, 'last_name', '')}").strip() or getattr(u, "username", "")
        citizen_national_id = (getattr(u, "national_id", "") or "").strip()
        citizen_phone = (getattr(u, "phone", "") or "").strip()

        tip = RewardTip.objects.create(
            citizen=u,
            citizen_name=citizen_name or "unknown",
            citizen_national_id=citizen_national_id or "unknown",
            citizen_phone=citizen_phone or "unknown",
            suspect_name=suspect_name,
            suspect_last_seen=suspect_last_seen,
            message=info,
            status=RewardTip.STATUS_SUBMITTED,
        )

        return Response({"id": tip.id, "status": tip.status}, status=status.HTTP_201_CREATED)


class OfficerReviewTip(APIView):
    permission_classes = [IsOfficerLevel]

    def post(self, request, tip_id: int):
        tip = get_object_or_404(RewardTip, id=tip_id)

        if tip.status != RewardTip.STATUS_SUBMITTED:
            return Response(
                {"detail": f"Tip is not in SUBMITTED state (current={tip.status})."},
                status=status.HTTP_409_CONFLICT,
            )

        action = (request.data.get("action") or request.data.get("decision") or "").lower().strip()
        if action not in ("approve", "reject"):
            return Response(
                {"detail": "action must be 'approve' or 'reject'."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        tip.reviewed_by_officer = request.user
        tip.officer_reviewed_at = timezone.now()
        tip.status = RewardTip.STATUS_OFFICER_APPROVED if action == "approve" else RewardTip.STATUS_OFFICER_REJECTED
        tip.save(update_fields=["status", "reviewed_by_officer", "officer_reviewed_at"])

        return Response({"id": tip.id, "status": tip.status}, status=status.HTTP_200_OK)


class DetectiveApproveTip(APIView):
    permission_classes = [IsDetectiveLevel]

    def post(self, request, tip_id: int):
        tip = get_object_or_404(RewardTip, id=tip_id)

        if tip.status != RewardTip.STATUS_OFFICER_APPROVED:
            return Response(
                {"detail": f"Tip is not in OFFICER_APPROVED state (current={tip.status})."},
                status=status.HTTP_409_CONFLICT,
            )

        tip.approved_by_detective = request.user
        tip.detective_approved_at = timezone.now()
        tip.approve_by_detective()

        return Response(
            {"id": tip.id, "status": tip.status, "unique_code": tip.unique_code},
            status=status.HTTP_200_OK,
        )


class RewardLookup(APIView):
    permission_classes = [IsPoliceRole]

    def get(self, request):
        citizen_national_id = (
            (request.query_params.get("national_id") or request.query_params.get("citizen_national_id") or "").strip()
        )
        unique_code = (request.query_params.get("code") or request.query_params.get("unique_code") or "").strip()

        if not citizen_national_id or not unique_code:
            return Response(
                {"detail": "national_id and code are required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        tip = (
            RewardTip.objects.filter(
                citizen_national_id=citizen_national_id,
                unique_code=unique_code,
                status=RewardTip.STATUS_DETECTIVE_APPROVED,
            )
            .order_by("-created_at")
            .first()
        )

        if not tip:
            return Response(
                {"detail": "No detective-approved tip found for the given national_id and code."},
                status=status.HTTP_404_NOT_FOUND,
            )

        suspect = Suspect.objects.filter(full_name__iexact=tip.suspect_name).order_by("-id").first()
        reward_amount_rials = suspect.reward_amount_rials if suspect else 0

        return Response(
            {
                "tip_id": tip.id,
                "reward_amount_rials": reward_amount_rials,
                "unique_code": tip.unique_code,
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
            },
            status=status.HTTP_200_OK,
        )