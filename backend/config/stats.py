from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from cases.models import Case
from suspects.models import Suspect
from rewards.models import RewardTip

class StatsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response({
            "cases_open": Case.objects.filter(status="OPEN").count(),
            "cases_closed": Case.objects.filter(status="CLOSED").count(),
            "most_wanted": sum(1 for s in Suspect.objects.all() if s.is_most_wanted),
            "tips_pending": RewardTip.objects.filter(status="SUBMITTED").count(),
        })
