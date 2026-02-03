from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from rbac.permissions import HasRole
from .models import RewardTip

class SubmitTip(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        tip = RewardTip.objects.create(
            citizen=request.user,
            suspect_name=request.data.get("suspect_name",""),
            info=request.data.get("info",""),
        )
        return Response({"id": tip.id, "status": tip.status}, status=201)

class OfficerReviewTip(APIView):
    permission_classes = [HasRole.with_roles("Officer","Admin")]

    def post(self, request, tip_id: int):
        action = request.data.get("action")  # "approve" or "reject"
        tip = RewardTip.objects.get(id=tip_id)
        if action == "reject":
            tip.status = "OFFICER_REJECTED"
        else:
            tip.status = "OFFICER_APPROVED"
        tip.save(update_fields=["status"])
        return Response({"id": tip.id, "status": tip.status})

class DetectiveApproveTip(APIView):
    permission_classes = [HasRole.with_roles("Detective","Admin")]

    def post(self, request, tip_id: int):
        tip = RewardTip.objects.get(id=tip_id)
        tip.approve_by_detective()
        return Response({"id": tip.id, "status": tip.status, "unique_code": tip.unique_code})

class RewardLookup(APIView):
    permission_classes = [HasRole.with_roles("Officer","Admin")]

    def get(self, request):
        national_id = request.query_params.get("national_id","")
        code = request.query_params.get("code","")
        tip = RewardTip.objects.filter(citizen__national_id=national_id, unique_code=code).first()
        if not tip:
            return Response({"detail":"Not found"}, status=404)
        return Response({
            "tip_id": tip.id,
            "citizen_id": tip.citizen_id,
            "status": tip.status,
            "suspect_name": tip.suspect_name,
        })
