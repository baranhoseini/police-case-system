from datetime import timedelta

from django.utils import timezone
from django.db.models import F, IntegerField, ExpressionWrapper
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from rbac.permissions import HasRole
from cases.models import Case
from .models import Suspect


class MostWantedList(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        cutoff = timezone.now() - timedelta(days=30)
        score_expr = ExpressionWrapper(F("max_l") * F("max_d"), output_field=IntegerField())

        qs = (
            Suspect.objects.filter(chase_started_at__lte=cutoff)
            .annotate(rank_score_db=score_expr)
            .order_by("-rank_score_db", "-id")
        )

        data = [
            {
                "id": s.id,
                "case_id": s.case_id,
                "full_name": s.full_name,
                "chase_started_at": s.chase_started_at,
                "max_l": s.max_l,
                "max_d": s.max_d,
                "rank_score": int(s.rank_score_db),
                "reward_rials": int(s.rank_score_db) * 20_000_000,
            }
            for s in qs
        ]
        return Response(data, status=status.HTTP_200_OK)


class CaseSuspects(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, case_id: int):
        try:
            case = Case.objects.get(id=case_id)
        except Case.DoesNotExist:
            return Response({"detail": "Case not found"}, status=status.HTTP_404_NOT_FOUND)

        qs = Suspect.objects.filter(case=case).order_by("-id")
        data = [
            {
                "id": s.id,
                "case_id": s.case_id,
                "full_name": s.full_name,
                "chase_started_at": s.chase_started_at,
                "max_l": s.max_l,
                "max_d": s.max_d,
                "rank_score": s.rank_score,
                "reward_rials": s.reward_amount_rials,
                "is_most_wanted": s.is_most_wanted,
            }
            for s in qs
        ]
        return Response(data, status=status.HTTP_200_OK)

    def post(self, request, case_id: int):
        self.permission_classes = [HasRole.with_roles("Officer", "Detective", "Admin")]
        for permission in self.get_permissions():
            permission.has_permission(request, self)

        full_name = (request.data.get("full_name") or "").strip()
        if not full_name:
            return Response({"detail": "full_name is required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            max_l = int(request.data.get("max_l", 1))
            max_d = int(request.data.get("max_d", 1))
        except (TypeError, ValueError):
            return Response({"detail": "max_l and max_d must be integers"}, status=status.HTTP_400_BAD_REQUEST)

        if max_l < 1 or max_d < 1:
            return Response({"detail": "max_l and max_d must be >= 1"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            case = Case.objects.get(id=case_id)
        except Case.DoesNotExist:
            return Response({"detail": "Case not found"}, status=status.HTTP_404_NOT_FOUND)

        suspect = Suspect.objects.create(case=case, full_name=full_name, max_l=max_l, max_d=max_d)
        return Response(
            {
                "id": suspect.id,
                "case_id": suspect.case_id,
                "full_name": suspect.full_name,
                "max_l": suspect.max_l,
                "max_d": suspect.max_d,
                "rank_score": suspect.rank_score,
                "reward_rials": suspect.reward_amount_rials,
                "is_most_wanted": suspect.is_most_wanted,
            },
            status=status.HTTP_201_CREATED,
        )


class SuspectRankUpdate(APIView):
    permission_classes = [HasRole.with_roles("Officer", "Detective", "Admin")]

    def patch(self, request, suspect_id: int):
        try:
            suspect = Suspect.objects.get(id=suspect_id)
        except Suspect.DoesNotExist:
            return Response({"detail": "Not found"}, status=status.HTTP_404_NOT_FOUND)

        max_l = request.data.get("max_l", None)
        max_d = request.data.get("max_d", None)

        update_fields = []
        if max_l is not None:
            try:
                max_l = int(max_l)
            except (TypeError, ValueError):
                return Response({"detail": "max_l must be an integer"}, status=status.HTTP_400_BAD_REQUEST)
            if max_l < 1:
                return Response({"detail": "max_l must be >= 1"}, status=status.HTTP_400_BAD_REQUEST)
            suspect.max_l = max_l
            update_fields.append("max_l")

        if max_d is not None:
            try:
                max_d = int(max_d)
            except (TypeError, ValueError):
                return Response({"detail": "max_d must be an integer"}, status=status.HTTP_400_BAD_REQUEST)
            if max_d < 1:
                return Response({"detail": "max_d must be >= 1"}, status=status.HTTP_400_BAD_REQUEST)
            suspect.max_d = max_d
            update_fields.append("max_d")

        if not update_fields:
            return Response({"detail": "Nothing to update"}, status=status.HTTP_400_BAD_REQUEST)

        suspect.save(update_fields=update_fields)
        return Response(
            {
                "id": suspect.id,
                "case_id": suspect.case_id,
                "full_name": suspect.full_name,
                "max_l": suspect.max_l,
                "max_d": suspect.max_d,
                "rank_score": suspect.rank_score,
                "reward_rials": suspect.reward_amount_rials,
                "is_most_wanted": suspect.is_most_wanted,
            },
            status=status.HTTP_200_OK,
        )
