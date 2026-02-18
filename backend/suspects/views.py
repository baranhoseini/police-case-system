from django.shortcuts import get_object_or_404
from django.utils.dateparse import parse_datetime
from django.utils import timezone
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from cases.models import Case
from config.permissions import HasRole
from .models import Suspect

POLICE_ROLES = ("Admin", "Cadet", "Officer", "Detective", "Chief", "Captain", "Supervisor")
IsPoliceRole = HasRole.with_roles(*POLICE_ROLES)
IsDetectiveLevel = HasRole.with_roles("Detective", "Admin", "Chief", "Captain", "Supervisor")


class MostWantedList(APIView):
    permission_classes = [IsPoliceRole]

    def get(self, request):
        qs = Suspect.objects.most_wanted().order_by("-max_l", "-max_d", "-chase_started_at")
        data = [
            {
                "id": s.id,
                "full_name": s.full_name,
                "case_id": s.case_id,
                "chase_started_at": s.chase_started_at,
                "max_l": s.max_l,
                "max_d": s.max_d,
                "is_most_wanted": s.is_most_wanted,
                "rank_score": s.rank_score,
                "reward_amount_rials": s.reward_amount_rials,
            }
            for s in qs
        ]
        return Response(data, status=status.HTTP_200_OK)


class CaseSuspects(APIView):
    def get_permissions(self):
        if self.request.method == "POST":
            return [IsDetectiveLevel()]
        return [IsPoliceRole()]

    def get(self, request, case_id: int):
        get_object_or_404(Case, id=case_id)
        suspects = Suspect.objects.filter(case_id=case_id).order_by("-id")
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
            }
            for s in suspects
        ]
        return Response(data, status=status.HTTP_200_OK)

    def post(self, request, case_id: int):
        case = get_object_or_404(Case, id=case_id)

        full_name = (request.data.get("full_name") or "").strip()
        if not full_name:
            return Response({"detail": "full_name is required."}, status=status.HTTP_400_BAD_REQUEST)

        chase_started_at = request.data.get("chase_started_at")
        dt = parse_datetime(chase_started_at) if chase_started_at else None
        if chase_started_at and not dt:
            return Response({"detail": "chase_started_at must be ISO datetime."}, status=status.HTTP_400_BAD_REQUEST)

        max_l = request.data.get("max_l", 1)
        max_d = request.data.get("max_d", 1)

        suspect = Suspect.objects.create(
            case=case,
            full_name=full_name,
            chase_started_at=dt or timezone.now(),
            max_l=max_l,
            max_d=max_d,
        )

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
            },
            status=status.HTTP_201_CREATED,
        )


class SuspectUpdate(APIView):
    permission_classes = [IsDetectiveLevel]

    def patch(self, request, suspect_id: int):
        suspect = get_object_or_404(Suspect, id=suspect_id)

        allowed = {"full_name", "chase_started_at", "max_l", "max_d"}
        updated = []

        for key, val in request.data.items():
            if key not in allowed:
                continue
            if key == "chase_started_at":
                dt = parse_datetime(val) if isinstance(val, str) else None
                if not dt:
                    return Response({"detail": "chase_started_at must be ISO datetime."}, status=status.HTTP_400_BAD_REQUEST)
                setattr(suspect, key, dt)
            else:
                setattr(suspect, key, val)
            updated.append(key)

        if not updated:
            return Response({"detail": "No valid fields provided."}, status=status.HTTP_400_BAD_REQUEST)

        suspect.save(update_fields=updated)

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
            },
            status=status.HTTP_200_OK,
        )
