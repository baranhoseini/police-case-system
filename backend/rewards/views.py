from django.shortcuts import get_object_or_404
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
    permission_classes = [IsAuthenticated]

    def post(self, request):
        suspect_name = (request.data.get("suspect_name") or "").strip()
        suspect_last_seen = (request.data.get("suspect_last_seen") or "").strip()
        message = (request.data.get("message") or "").strip()

        citizen_name = (request.data.get("citizen_name") or "").strip()
        citizen_national_id = (request.data.get("citizen_national_id") or "").strip()
        citizen_phone = (request.data.get("citizen_phone") or "").strip()

        missing = []
        if not suspect_name:
            missing.append("suspect_name")
        if not suspect_last_seen:
            missing.append("suspect_last_seen")
        if not message:
            missing.append("message")
        if not citizen_name:
            missing.append("citizen_name")
        if not citizen_national_id:
            missing.append("citizen_national_id")
        if not citizen_phone:
            missing.append("citizen_phone")

        if missing:
            return Response(
                {"detail": "Missing required fields.", "missing": missing},
                status=status.HTTP_400_BAD_REQUEST,
            )

        submitted_value = getattr(RewardTip, "STATUS_SUBMITTED", "SUBMITTED")

        tip = RewardTip.objects.create(
            citizen=request.user,
            citizen_name=citizen_name,
            citizen_national_id=citizen_national_id,
            citizen_phone=citizen_phone,
            suspect_name=suspect_name,
            suspect_last_seen=suspect_last_seen,
            message=message,
            status=submitted_value,
        )

        return Response(
            {"tip_id": tip.id, "status": tip.status},
            status=status.HTTP_201_CREATED,
        )


class OfficerReviewTip(APIView):
    permission_classes = [IsOfficerLevel]

    def post(self, request, tip_id: int):
        tip = get_object_or_404(RewardTip, id=tip_id)

        submitted_value = getattr(RewardTip, "STATUS_SUBMITTED", "SUBMITTED")
        officer_approved_value = getattr(RewardTip, "STATUS_OFFICER_APPROVED", "OFFICER_APPROVED")
        officer_rejected_value = getattr(RewardTip, "STATUS_OFFICER_REJECTED", "OFFICER_REJECTED")

        if tip.status != submitted_value:
            return Response(
                {"detail": f"Tip is not in SUBMITTED state (current={tip.status})."},
                status=status.HTTP_409_CONFLICT,
            )

        decision = (request.data.get("decision") or "").lower().strip()
        if decision not in ("approve", "reject"):
            return Response(
                {"detail": "decision must be 'approve' or 'reject'."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        tip.status = officer_approved_value if decision == "approve" else officer_rejected_value
        tip.save(update_fields=["status"])

        return Response({"tip_id": tip.id, "status": tip.status}, status=status.HTTP_200_OK)


class DetectiveApproveTip(APIView):
    permission_classes = [IsDetectiveLevel]

    def post(self, request, tip_id: int):
        tip = get_object_or_404(RewardTip, id=tip_id)

        officer_approved_value = getattr(RewardTip, "STATUS_OFFICER_APPROVED", "OFFICER_APPROVED")

        if tip.status != officer_approved_value:
            return Response(
                {"detail": f"Tip is not in OFFICER_APPROVED state (current={tip.status})."},
                status=status.HTTP_409_CONFLICT,
            )

        tip.approve_by_detective()
        return Response(
            {"tip_id": tip.id, "status": tip.status, "unique_code": tip.unique_code},
            status=status.HTTP_200_OK,
        )


class RewardLookup(APIView):
    permission_classes = [IsPoliceRole]

    def get(self, request):
        citizen_national_id = (request.query_params.get("citizen_national_id") or "").strip()
        unique_code = (request.query_params.get("unique_code") or "").strip()

        if not citizen_national_id or not unique_code:
            return Response(
                {"detail": "citizen_national_id and unique_code are required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        detective_approved_value = getattr(RewardTip, "STATUS_DETECTIVE_APPROVED", "DETECTIVE_APPROVED")

        tip = (
            RewardTip.objects.filter(
                citizen_national_id=citizen_national_id,
                unique_code=unique_code,
                status=detective_approved_value,
            )
            .order_by("-created_at")
            .first()
        )

        if not tip:
            return Response(
                {"detail": "No detective-approved tip found for the given citizen_national_id and unique_code."},
                status=status.HTTP_404_NOT_FOUND,
            )

        suspect = Suspect.objects.filter(full_name__iexact=tip.suspect_name).order_by("-id").first()
        reward_amount_rials = suspect.reward_amount_rials if suspect else 0

        return Response(
            {
                "reward_amount_rials": reward_amount_rials,
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
