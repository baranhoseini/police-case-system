from django.db.models import Count
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from cases.models import Case
from evidence.models import Evidence
from rewards.models import RewardTip
from suspects.models import Suspect


class StatsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        cases_by_status_qs = (
            Case.objects.values("status")
            .annotate(count=Count("id"))
            .order_by("status")
        )
        cases_by_status = {row["status"]: row["count"] for row in cases_by_status_qs}

        tips_by_status_qs = (
            RewardTip.objects.values("status")
            .annotate(count=Count("id"))
            .order_by("status")
        )
        tips_by_status = {row["status"]: row["count"] for row in tips_by_status_qs}

        data = {
            "cases_total": Case.objects.count(),
            "cases_by_status": cases_by_status,
            "cases_open": Case.objects.filter(status="OPEN").count(),
            "cases_closed": Case.objects.filter(status="CLOSED").count(),
            "evidence_total": Evidence.objects.count(),
            "suspects_total": Suspect.objects.count(),
            "most_wanted_total": Suspect.objects.most_wanted().count(),
            "most_wanted": Suspect.objects.most_wanted().count(),
            "tips_total": RewardTip.objects.count(),
            "tips_by_status": tips_by_status,
            "tips_pending": RewardTip.objects.filter(status=RewardTip.STATUS_SUBMITTED).count(),
        }
        return Response(data)
