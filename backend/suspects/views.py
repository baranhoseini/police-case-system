from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import Suspect

class MostWantedList(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        qs = [s for s in Suspect.objects.all() if s.is_most_wanted]
        qs.sort(key=lambda s: s.rank_score, reverse=True)
        data = [{
            "id": s.id,
            "case_id": s.case_id,
            "full_name": s.full_name,
            "rank_score": s.rank_score,
            "reward_rials": s.reward_amount_rials,
        } for s in qs]
        return Response(data)
