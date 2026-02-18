# suspects/views.py
from datetime import timedelta

from django.shortcuts import get_object_or_404
from django.utils import timezone

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from cases.models import Case
from config.permissions import HasRole
from .models import Suspect

# All police roles available in your system:
# Admin, Cadet, Chief, Detective, Officer, Supervisor
POLICE_ROLES = ("Admin", "Cadet", "Chief", "Detective", "Officer", "Supervisor")

# Permission shortcuts
IsPoliceRole = HasRole.with_roles(*POLICE_ROLES)
IsDetectiveLevel = HasRole.with_roles("Detective", "Admin", "Chief", "Supervisor")


class MostWantedList(APIView):
    """
    GET /api/suspects/most-wanted/

    In this project Suspect model does NOT have:
      - under_chase
      - created_at
      - rank
    It has:
      - chase_started_at (datetime)
      - max_l (int)
      - max_d (int)
      - properties: rank_score, reward_amount_rials

    We interpret "most wanted" as: chase_started_at <= now - 30 days
    (same as SuspectQuerySet.most_wanted()).
    """
    permission_classes = [IsPoliceRole]

    def get(self, request):
        # Use the model's queryset helper. It already applies 30 days cutoff.
        qs = Suspect.objects.most_wanted().select_related("case").order_by("chase_started_at")

        data = [
            {
                "id": s.id,
                "full_name": s.full_name,
                "case_id": s.case_id,
                "chase_started_at": s.chase_started_at,
                "max_l": s.max_l,
                "max_d": s.max_d,
                "rank_score": s.rank_score,
                "reward_amount_rials": s.reward_amount_rials,
                "is_most_wanted": s.is_most_wanted,
            }
            for s in qs
        ]

        return Response(data, status=status.HTTP_200_OK)


class CaseSuspects(APIView):
    """
    GET  /api/suspects/case/<case_id>/
      - Allowed for all police roles

    POST /api/suspects/case/<case_id>/
      - Allowed only for Detective/Admin/Chief/Supervisor

    Notes:
      Suspect model fields allowed:
        - full_name (required)
        - chase_started_at (optional)
        - max_l (optional)
        - max_d (optional)
        - case (FK) set from URL
    """

    def get_permissions(self):
        if self.request.method == "POST":
            return [IsDetectiveLevel()]
        return [IsPoliceRole()]

    def get(self, request, case_id: int):
        get_object_or_404(Case, id=case_id)

        suspects = (
            Suspect.objects.filter(case_id=case_id)
            .order_by("-chase_started_at", "-id")
        )

        data = [
            {
                "id": s.id,
                "full_name": s.full_name,
                "case_id": s.case_id,
                "chase_started_at": s.chase_started_at,
                "max_l": s.max_l,
                "max_d": s.max_d,
                "rank_score": s.rank_score,
                "reward_amount_rials": s.reward_amount_rials,
                "is_most_wanted": s.is_most_wanted,
            }
            for s in suspects
        ]
        return Response(data, status=status.HTTP_200_OK)

    def post(self, request, case_id: int):
        case = get_object_or_404(Case, id=case_id)

        full_name = request.data.get("full_name")
        if not full_name:
            return Response({"detail": "full_name is required."}, status=status.HTTP_400_BAD_REQUEST)

        payload = {"case": case, "full_name": full_name}

        # Optional, valid fields only (based on your Suspect model)
        if "chase_started_at" in request.data and request.data.get("chase_started_at"):
            payload["chase_started_at"] = request.data.get("chase_started_at")

        if "max_l" in request.data and request.data.get("max_l") is not None:
            payload["max_l"] = request.data.get("max_l")

        if "max_d" in request.data and request.data.get("max_d") is not None:
            payload["max_d"] = request.data.get("max_d")

        suspect = Suspect.objects.create(**payload)

        return Response(
            {
                "id": suspect.id,
                "full_name": suspect.full_name,
                "case_id": suspect.case_id,
                "chase_started_at": suspect.chase_started_at,
                "max_l": suspect.max_l,
                "max_d": suspect.max_d,
                "rank_score": suspect.rank_score,
                "reward_amount_rials": suspect.reward_amount_rials,
                "is_most_wanted": suspect.is_most_wanted,
            },
            status=status.HTTP_201_CREATED,
        )


class SuspectRankUpdate(APIView):
    """
    PATCH /api/suspects/<suspect_id>/rank/

    In your current Suspect model, there is no 'rank' or 'under_chase'.
    Rank is derived: rank_score = max_l * max_d

    So allowed updates:
      - max_l
      - max_d
      - chase_started_at (optional, if you want to adjust when the chase began)
    """
    permission_classes = [IsDetectiveLevel]

    def patch(self, request, suspect_id: int):
        suspect = get_object_or_404(Suspect, id=suspect_id)

        allowed = {"max_l", "max_d", "chase_started_at"}
        update_fields = []

        for key, val in request.data.items():
            if key in allowed:
                setattr(suspect, key, val)
                update_fields.append(key)

        if not update_fields:
            return Response(
                {"detail": "No valid fields provided. Allowed: max_l, max_d, chase_started_at."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        suspect.save(update_fields=update_fields)

        return Response(
            {
                "id": suspect.id,
                "full_name": suspect.full_name,
                "case_id": suspect.case_id,
                "chase_started_at": suspect.chase_started_at,
                "max_l": suspect.max_l,
                "max_d": suspect.max_d,
                "rank_score": suspect.rank_score,
                "reward_amount_rials": suspect.reward_amount_rials,
                "is_most_wanted": suspect.is_most_wanted,
            },
            status=status.HTTP_200_OK,
        )
