from datetime import datetime

from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework import status
from rest_framework.permissions import BasePermission, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from cases.models import Case
from rbac.permissions import user_has_role
from .models import Suspect


class IsPoliceRole(BasePermission):
    def has_permission(self, request, view):
        return any(
            user_has_role(request.user, r)
            for r in ["Officer", "Patrol", "Detective", "Sergeant", "Supervisor", "Captain", "Chief", "Admin"]
        )


def _parse_dt(val):
    if not val:
        return None
    if isinstance(val, datetime):
        return val
    try:
        return datetime.fromisoformat(val)
    except Exception:
        return None


def _serialize(suspect: Suspect):
    return {
        "id": suspect.id,
        "full_name": suspect.full_name,
        "national_id": getattr(suspect, "national_id", ""),
        "phone": getattr(suspect, "phone", ""),
        "photo_url": getattr(suspect, "photo_url", ""),
        "case_id": suspect.case_id,
        "chase_started_at": suspect.chase_started_at,
        "max_l": suspect.max_l,
        "max_d": suspect.max_d,
        "is_most_wanted": suspect.is_most_wanted,
        "rank_score": suspect.rank_score,
        "reward_amount_rials": suspect.reward_amount_rials,
        "reward_rials": suspect.reward_amount_rials,
    }


class MostWantedList(APIView):
    # Visible to all authenticated users
    permission_classes = [IsAuthenticated]

    def get(self, request):
        suspects = list(Suspect.objects.most_wanted().select_related("case").all())
        data = [_serialize(s) for s in suspects]
        data.sort(key=lambda x: x.get("rank_score", 0), reverse=True)
        return Response(data, status=status.HTTP_200_OK)


class CaseSuspects(APIView):
    permission_classes = [IsPoliceRole]

    def get(self, request, case_id):
        case = get_object_or_404(Case, id=case_id)
        qs = Suspect.objects.filter(case=case).order_by("-created_at")
        return Response([_serialize(s) for s in qs], status=status.HTTP_200_OK)

    def post(self, request, case_id):
        case = get_object_or_404(Case, id=case_id)
        full_name = (request.data.get("full_name") or "").strip()
        if not full_name:
            return Response({"detail": "full_name is required"}, status=status.HTTP_400_BAD_REQUEST)

        chase_started_at = _parse_dt(request.data.get("chase_started_at")) or timezone.now()
        max_l = int(request.data.get("max_l") or 0)
        max_d = int(request.data.get("max_d") or 1)

        suspect = Suspect.objects.create(
            case=case,
            full_name=full_name,
            national_id=(request.data.get("national_id") or "").strip(),
            phone=(request.data.get("phone") or "").strip(),
            photo_url=(request.data.get("photo_url") or "").strip(),
            chase_started_at=chase_started_at,
            max_l=max_l,
            max_d=max_d,
        )
        return Response(_serialize(suspect), status=status.HTTP_201_CREATED)


class SuspectUpdate(APIView):
    permission_classes = [IsPoliceRole]

    def patch(self, request, suspect_id):
        suspect = get_object_or_404(Suspect, id=suspect_id)

        allowed = {"full_name", "national_id", "phone", "photo_url", "chase_started_at", "max_l", "max_d"}
        for k in request.data.keys():
            if k not in allowed:
                return Response({"detail": f"Field {k} not allowed"}, status=status.HTTP_400_BAD_REQUEST)

        if "full_name" in request.data:
            suspect.full_name = (request.data.get("full_name") or "").strip()

        if "national_id" in request.data:
            suspect.national_id = (request.data.get("national_id") or "").strip()

        if "phone" in request.data:
            suspect.phone = (request.data.get("phone") or "").strip()

        if "photo_url" in request.data:
            suspect.photo_url = (request.data.get("photo_url") or "").strip()

        if "chase_started_at" in request.data:
            dt = _parse_dt(request.data.get("chase_started_at"))
            if not dt:
                return Response({"detail": "Invalid chase_started_at"}, status=status.HTTP_400_BAD_REQUEST)
            suspect.chase_started_at = dt

        if "max_l" in request.data:
            suspect.max_l = int(request.data.get("max_l") or 0)

        if "max_d" in request.data:
            suspect.max_d = int(request.data.get("max_d") or 1)

        suspect.save()
        return Response(_serialize(suspect), status=status.HTTP_200_OK)
