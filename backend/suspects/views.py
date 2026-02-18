# suspects/views.py
from datetime import timedelta

from django.db.models import Max
from django.shortcuts import get_object_or_404
from django.utils import timezone

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from cases.models import Case
from config.permissions import HasRole
from .models import Suspect

# All police roles available in your system (from your output):
# Admin, Cadet, Chief, Detective, Officer, Supervisor
POLICE_ROLES = ("Admin", "Cadet", "Chief", "Detective", "Officer", "Supervisor")

# Permission shortcuts
IsPoliceRole = HasRole.with_roles(*POLICE_ROLES)
IsDetectiveLevel = HasRole.with_roles("Detective", "Admin", "Chief", "Supervisor")


class MostWantedList(APIView):
    """
    GET /api/suspects/most-wanted/
    Returns suspects that have been under chase for at least 30 days,
    ordered by rank and creation date (descending), plus a computed reward_amount.
    """
    permission_classes = [IsPoliceRole]

    def get(self, request):
        cutoff = timezone.now() - timedelta(days=30)

        # NOTE:
        # This assumes your Suspect model has:
        # - under_chase (bool)
        # - created_at (datetime)
        # - rank (int/float)
        # - max_d (int)
        qs = (
            Suspect.objects.filter(under_chase=True, created_at__lte=cutoff)
            .order_by("-rank", "-created_at")
        )

        max_l = qs.aggregate(m=Max("rank"))["m"] or 0
        max_d = Suspect.objects.aggregate(m=Max("max_d"))["m"] or 0

        items = []
        for s in qs:
            # Reward formula (based on your current logic):
            # reward_amount = round((rank / max_rank) * max_d)
            if max_l and max_d and s.rank:
                reward_amount = int(round((float(s.rank) / float(max_l)) * float(max_d)))
            else:
                reward_amount = 0

            items.append(
                {
                    "id": s.id,
                    "full_name": s.full_name,
                    "photo_url": getattr(s, "photo_url", None),
                    "age": getattr(s, "age", None),
                    "rank": s.rank,
                    "under_chase": s.under_chase,
                    "reward_amount": reward_amount,
                    "case_id": getattr(s, "case_id", None),
                    "created_at": s.created_at,
                }
            )

        return Response(items, status=status.HTTP_200_OK)


class CaseSuspects(APIView):
    """
    GET  /api/suspects/case/<case_id>/
      - Allowed for all police roles

    POST /api/suspects/case/<case_id>/
      - Allowed only for Detective/Admin/Chief/Supervisor
    """

    def get_permissions(self):
        # POST is restricted
        if self.request.method == "POST":
            return [IsDetectiveLevel()]
        # GET is open to all police roles
        return [IsPoliceRole()]

    def get(self, request, case_id: int):
        get_object_or_404(Case, id=case_id)

        suspects = Suspect.objects.filter(case_id=case_id).order_by("-created_at")

        data = [
            {
                "id": s.id,
                "full_name": s.full_name,
                "photo_url": getattr(s, "photo_url", None),
                "age": getattr(s, "age", None),
                "rank": s.rank,
                "under_chase": s.under_chase,
                "created_at": s.created_at,
            }
            for s in suspects
        ]
        return Response(data, status=status.HTTP_200_OK)

    def post(self, request, case_id: int):
        # IMPORTANT:
        # We do NOT manually call has_permission() here.
        # DRF runs get_permissions() + permission checks automatically.
        # This prevents the common "permission not enforced" bug.
        case = get_object_or_404(Case, id=case_id)

        full_name = request.data.get("full_name")
        photo_url = request.data.get("photo_url")
        age = request.data.get("age")

        if not full_name:
            return Response({"detail": "full_name is required."}, status=status.HTTP_400_BAD_REQUEST)

        payload = {
            "case": case,
            "full_name": full_name,
        }

        # Optional fields (set only if provided)
        if photo_url is not None:
            payload["photo_url"] = photo_url
        if age is not None:
            payload["age"] = age

        # Optional model fields (safe set)
        if "rank" in request.data:
            payload["rank"] = request.data.get("rank")
        if "under_chase" in request.data:
            payload["under_chase"] = request.data.get("under_chase")
        if "max_d" in request.data:
            payload["max_d"] = request.data.get("max_d")
        if "max_l" in request.data:
            payload["max_l"] = request.data.get("max_l")

        suspect = Suspect.objects.create(**payload)

        return Response(
            {
                "id": suspect.id,
                "full_name": suspect.full_name,
                "photo_url": getattr(suspect, "photo_url", None),
                "age": getattr(suspect, "age", None),
                "rank": suspect.rank,
                "under_chase": suspect.under_chase,
                "case_id": suspect.case_id,
                "created_at": suspect.created_at,
            },
            status=status.HTTP_201_CREATED,
        )


class SuspectRankUpdate(APIView):
    """
    PATCH /api/suspects/<suspect_id>/rank/
    Update allowed fields (rank/max_l/max_d/under_chase) for a suspect.
    Restricted to Detective/Admin/Chief/Supervisor.
    """
    permission_classes = [IsDetectiveLevel]

    def patch(self, request, suspect_id: int):
        suspect = get_object_or_404(Suspect, id=suspect_id)

        allowed = {"rank", "max_l", "max_d", "under_chase"}
        update_fields = []

        for key, val in request.data.items():
            if key in allowed:
                setattr(suspect, key, val)
                update_fields.append(key)

        if not update_fields:
            return Response(
                {"detail": "No valid fields provided. Allowed: rank, max_l, max_d, under_chase."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        suspect.save(update_fields=update_fields)

        return Response(
            {
                "id": suspect.id,
                "full_name": suspect.full_name,
                "rank": suspect.rank,
                "max_l": getattr(suspect, "max_l", None),
                "max_d": getattr(suspect, "max_d", None),
                "under_chase": suspect.under_chase,
            },
            status=status.HTTP_200_OK,
        )
