from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from rbac.permissions import HasRole
from .models import RewardTip


class SubmitTip(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        suspect_name = (request.data.get("suspect_name") or "").strip()
        info = (request.data.get("info") or "").strip()

        if not suspect_name:
            return Response({"detail": "suspect_name is required"}, status=status.HTTP_400_BAD_REQUEST)
        if not info:
            return Response({"detail": "info is required"}, status=status.HTTP_400_BAD_REQUEST)

        tip = RewardTip.objects.create(
            citizen=request.user,
            suspect_name=suspect_name,
            info=info,
        )
        return Response({"id": tip.id, "status": tip.status}, status=status.HTTP_201_CREATED)


class OfficerReviewTip(APIView):
    permission_classes = [HasRole.with_roles("Officer", "Admin")]

    def post(self, request, tip_id: int):
        action = (request.data.get("action") or "").strip().lower()
        if action not in {"approve", "reject"}:
            return Response({"detail": "action must be 'approve' or 'reject'"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            tip = RewardTip.objects.get(id=tip_id)
        except RewardTip.DoesNotExist:
            return Response({"detail": "Not found"}, status=status.HTTP_404_NOT_FOUND)

        if tip.status != "SUBMITTED":
            return Response(
                {"detail": f"Cannot review tip in status {tip.status}"},
                status=status.HTTP_409_CONFLICT,
            )

        tip.status = "OFFICER_REJECTED" if action == "reject" else "OFFICER_APPROVED"
        tip.save(update_fields=["status"])
        return Response({"id": tip.id, "status": tip.status}, status=status.HTTP_200_OK)


class DetectiveApproveTip(APIView):
    permission_classes = [HasRole.with_roles("Detective", "Admin")]

    def post(self, request, tip_id: int):
        try:
            tip = RewardTip.objects.get(id=tip_id)
        except RewardTip.DoesNotExist:
            return Response({"detail": "Not found"}, status=status.HTTP_404_NOT_FOUND)

        if tip.status != "OFFICER_APPROVED":
            return Response(
                {"detail": f"Cannot detective-approve tip in status {tip.status}"},
                status=status.HTTP_409_CONFLICT,
            )

        tip.approve_by_detective()
        return Response(
            {"id": tip.id, "status": tip.status, "unique_code": tip.unique_code},
            status=status.HTTP_200_OK,
        )


class RewardLookup(APIView):
    permission_classes = [HasRole.with_roles("Officer", "Admin")]

    def get(self, request):
        national_id = (request.query_params.get("national_id") or "").strip()
        code = (request.query_params.get("code") or "").strip()

        if not national_id or not code:
            return Response(
                {"detail": "national_id and code are required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        tip = RewardTip.objects.filter(
            citizen__national_id=national_id,
            unique_code=code,
            status="DETECTIVE_APPROVED",
        ).first()

        if not tip:
            return Response({"detail": "Not found"}, status=status.HTTP_404_NOT_FOUND)

        return Response(
            {
                "tip_id": tip.id,
                "citizen_id": tip.citizen_id,
                "status": tip.status,
                "suspect_name": tip.suspect_name,
            },
            status=status.HTTP_200_OK,
        )
