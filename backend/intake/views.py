from django.db.models import Q
from django.db import transaction
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from rbac.permissions import IsCadetRole, IsOfficerRole, user_has_role
from cases.models import Case, CaseComplainant, CaseNotification

from .models import Complaint, ComplaintStatus
from .serializers import (
    CadetReviewSerializer,
    ComplaintCreateSerializer,
    ComplaintSerializer,
    OfficerReviewSerializer,
    ResubmitSerializer,
)


class ComplaintViewSet(ModelViewSet):
    queryset = Complaint.objects.all().order_by("-created_at")
    serializer_class = ComplaintSerializer
    permission_classes = [IsAuthenticated]

    def get_permissions(self):
        if self.action in {"cadet_inbox", "cadet_review"}:
            return [IsAuthenticated(), IsCadetRole()]
        if self.action in {"officer_inbox", "officer_review"}:
            return [IsAuthenticated(), IsOfficerRole()]
        return [IsAuthenticated()]

    def get_queryset(self):
        user = self.request.user
        if user.is_superuser or user.is_staff or user_has_role(user, "Admin"):
            return Complaint.objects.all().order_by("-created_at")

        if user_has_role(user, "Cadet"):
            return Complaint.objects.filter(
                Q(status__in=[ComplaintStatus.SUBMITTED, ComplaintStatus.OFFICER_DEFECT])
                | Q(cadet=user)
            ).order_by("-created_at")

        if user_has_role(user, "Officer"):
            return Complaint.objects.filter(
                Q(status=ComplaintStatus.CADET_APPROVED) | Q(officer=user)
            ).order_by("-created_at")

        return Complaint.objects.filter(created_by=user).order_by("-created_at")

    def get_serializer_class(self):
        if self.action == "create":
            return ComplaintCreateSerializer
        if self.action == "resubmit":
            return ResubmitSerializer
        if self.action == "cadet_review":
            return CadetReviewSerializer
        if self.action == "officer_review":
            return OfficerReviewSerializer
        return ComplaintSerializer

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    @action(detail=True, methods=["post"])
    def resubmit(self, request, pk=None):
        complaint = self.get_object()
        is_adminish = (
            request.user.is_superuser
            or request.user.is_staff
            or user_has_role(request.user, "Admin")
        )
        if complaint.created_by != request.user and not is_adminish:
            return Response({"detail": "Not allowed."}, status=status.HTTP_403_FORBIDDEN)

        if complaint.status == ComplaintStatus.INVALIDATED:
            return Response(
                {"detail": "Complaint is invalidated and cannot be resubmitted."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        serializer = self.get_serializer(complaint, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(
            status=ComplaintStatus.SUBMITTED,
            cadet_error_message="",
            officer_error_message="",
        )
        return Response(ComplaintSerializer(complaint).data)

    @action(detail=False, methods=["get"])
    def cadet_inbox(self, request):
        qs = Complaint.objects.filter(
            status__in=[ComplaintStatus.SUBMITTED, ComplaintStatus.OFFICER_DEFECT]
        ).filter(Q(cadet__isnull=True) | Q(cadet=request.user)).order_by("-created_at")
        return Response(ComplaintSerializer(qs, many=True).data)

    @action(detail=True, methods=["post"])
    def cadet_review(self, request, pk=None):
        complaint = self.get_object()

        is_adminish = (
            request.user.is_superuser
            or request.user.is_staff
            or user_has_role(request.user, "Admin")
        )
        if complaint.cadet and complaint.cadet_id != request.user.id and not is_adminish:
            return Response({"detail": "Not allowed."}, status=status.HTTP_403_FORBIDDEN)

        if complaint.status not in [ComplaintStatus.SUBMITTED, ComplaintStatus.OFFICER_DEFECT]:
            return Response(
                {"detail": f"Cannot cadet-review complaint in status {complaint.status}."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        complaint.cadet = request.user

        if serializer.validated_data["status"] == "approve":
            complaint.status = ComplaintStatus.CADET_APPROVED
            complaint.cadet_error_message = ""
        else:
            complaint.status = ComplaintStatus.NEEDS_FIX
            complaint.bad_submission_count += 1
            complaint.cadet_error_message = serializer.validated_data.get("error_message", "")
            complaint.invalidate_if_needed()

        complaint.save()
        return Response(ComplaintSerializer(complaint).data)

    @action(detail=False, methods=["get"])
    def officer_inbox(self, request):
        qs = Complaint.objects.filter(status=ComplaintStatus.CADET_APPROVED).filter(
            Q(officer__isnull=True) | Q(officer=request.user)
        ).order_by("-created_at")
        return Response(ComplaintSerializer(qs, many=True).data)

    @action(detail=True, methods=["post"])
    def officer_review(self, request, pk=None):
        complaint = self.get_object()

        is_adminish = (
            request.user.is_superuser
            or request.user.is_staff
            or user_has_role(request.user, "Admin")
        )
        if complaint.officer and complaint.officer_id != request.user.id and not is_adminish:
            return Response({"detail": "Not allowed."}, status=status.HTTP_403_FORBIDDEN)

        if complaint.status != ComplaintStatus.CADET_APPROVED:
            return Response(
                {"detail": f"Cannot officer-review complaint in status {complaint.status}."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        complaint.officer = request.user

        if serializer.validated_data["status"] == "approve":
            if complaint.case_id:
                return Response({"detail": "Case already created for this complaint"}, status=status.HTTP_400_BAD_REQUEST)

            payload = complaint.payload or {}
            title = (payload.get("title") or payload.get("case_title") or f"Complaint {complaint.id}").strip()
            description = payload.get("description") or payload.get("case_description") or ""
            try:
                crime_level = int(payload.get("crime_level") or 1)
            except Exception:
                crime_level = 1
            crime_level = max(1, min(4, crime_level))

            with transaction.atomic():
                case = Case.objects.create(
                    title=title,
                    description=description,
                    crime_level=crime_level,
                    details=payload,
                    created_by=complaint.created_by,
                    status="OPEN",
                )
                CaseComplainant.objects.get_or_create(
                    case=case,
                    user=complaint.created_by,
                    defaults={"status": CaseComplainant.STATUS_APPROVED},
                )
                CaseNotification.objects.create(case=case, message="Case formed from complaint")
                complaint.case = case
                complaint.status = ComplaintStatus.OFFICER_APPROVED
                complaint.officer_error_message = ""
                complaint.save()
        else:
            complaint.status = ComplaintStatus.OFFICER_DEFECT
            complaint.officer_error_message = serializer.validated_data.get("error_message", "")
            complaint.save()

        return Response(ComplaintSerializer(complaint).data)
